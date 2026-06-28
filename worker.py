import asyncio
import json
import structlog
from typing import Dict, Any
from arq.connections import RedisSettings
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import AsyncSessionLocal, redis_pool
from app.db.repositories import TaskRepository, AgentTraceRepository
from app.agents.graph import build_graph
from app.agents.checkpointer import get_checkpointer
from app.observability.tracing import setup_tracing

setup_logging(settings.LOG_LEVEL)
logger = structlog.get_logger(__name__)

async def publish_event(task_id: str, event_type: str, data: Any):
    client = Redis(connection_pool=redis_pool)
    channel = f"task_events:{task_id}"
    payload = json.dumps({"type": event_type, "data": data})
    await client.publish(channel, payload)
    await client.aclose()

async def execute_agent_task(ctx: Dict[Any, Any], task_id: str, prompt: str, workspace_id: str):
    logger.info("worker_task_started", task_id=task_id)
    setup_tracing()
    
    async with AsyncSessionLocal() as session:
        task_repo = TaskRepository(session)
        trace_repo = AgentTraceRepository(session)
        
        await task_repo.update_task_status(task_id, "RUNNING")
        await publish_event(task_id, "STATUS", "RUNNING")
        
        try:
            checkpointer = await get_checkpointer()
            workflow = build_graph()
            graph = workflow.compile(checkpointer=checkpointer)
            
            initial_state = {
                "messages": [HumanMessage(content=prompt)],
                "workspace_id": workspace_id,
                "current_step": 0
            }
            
            config = {"configurable": {"thread_id": task_id}}
            
            async for state_update in graph.astream(initial_state, config=config, stream_mode="updates"):
                for node_name, state in state_update.items():
                    logger.info("graph_node_executed", task_id=task_id, node=node_name)
                    await publish_event(task_id, "NODE_COMPLETE", {"node": node_name})
                    
                    # Store trace in DB (full state serialization)
                    # For safety, we serialize messages to dicts to avoid JSON encode issues
                    serialized_messages = []
                    if "messages" in state:
                        for msg in state["messages"]:
                            serialized_messages.append({"type": msg.type, "content": msg.content})
                    
                    await trace_repo.save_trace(
                        task_id=task_id,
                        node_name=node_name,
                        input_state={}, # Omitted for brevity in logs, but could capture full prior state
                        output_state={"step": state.get("current_step", 0), "messages": serialized_messages} 
                    )

            final_state = graph.get_state(config)
            
            if final_state.next:
                await task_repo.update_task_status(task_id, "INTERRUPTED")
                await publish_event(task_id, "STATUS", "INTERRUPTED")
            else:
                final_output = final_state.values.get("messages", [])[-1].content if final_state.values.get("messages") else "Done"
                await task_repo.update_task_status(task_id, "COMPLETED", final_output)
                await publish_event(task_id, "STATUS", "COMPLETED")
                await publish_event(task_id, "END_STREAM", True)

        except Exception as e:
            logger.error("worker_task_failed", task_id=task_id, error=str(e))
            await task_repo.update_task_status(task_id, "FAILED", str(e))
            await publish_event(task_id, "STATUS", "FAILED")
            await publish_event(task_id, "END_STREAM", True)

async def resume_agent_task(ctx: Dict[Any, Any], task_id: str, action: str):
    logger.info("worker_task_resumed", task_id=task_id, action=action)
    
    async with AsyncSessionLocal() as session:
        task_repo = TaskRepository(session)
        
        try:
            checkpointer = await get_checkpointer()
            workflow = build_graph()
            graph = workflow.compile(checkpointer=checkpointer)
            
            config = {"configurable": {"thread_id": task_id}}
            resume_data = "approve" if action == "approve" else "reject"
            
            async for state_update in graph.astream(Command(resume=resume_data), config=config, stream_mode="updates"):
                 for node_name, state in state_update.items():
                    await publish_event(task_id, "NODE_COMPLETE", {"node": node_name})
                    
            final_state = graph.get_state(config)
            if final_state.next:
                await task_repo.update_task_status(task_id, "INTERRUPTED")
                await publish_event(task_id, "STATUS", "INTERRUPTED")
            else:
                final_output = final_state.values.get("messages", [])[-1].content if final_state.values.get("messages") else "Done"
                await task_repo.update_task_status(task_id, "COMPLETED", final_output)
                await publish_event(task_id, "STATUS", "COMPLETED")
                await publish_event(task_id, "END_STREAM", True)

        except Exception as e:
            logger.error("worker_resume_failed", task_id=task_id, error=str(e))
            await task_repo.update_task_status(task_id, "FAILED", str(e))

async def startup(ctx):
    pass

async def shutdown(ctx):
    pass

class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = [execute_agent_task, resume_agent_task]
    on_startup = startup
    on_shutdown = shutdown
