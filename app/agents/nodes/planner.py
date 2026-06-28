import json
import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.llm.router import get_llm_router
from app.llm.prompts import PLANNER_SYSTEM_PROMPT
from app.agents.state import AgentState
from app.core.database import AsyncSessionLocal
from app.memory.vector_store import VectorStore
from app.memory.graph_store import GraphStore
from app.memory.manager import MemoryManager

logger = structlog.get_logger(__name__)

async def plan_node(state: AgentState) -> Dict[str, Any]:
    """Generates a plan based on the user prompt and previous messages."""
    logger.info("node_plan_start")
    
    router = get_llm_router()
    
    # Retrieve memory context
    memory_context = ""
    try:
        async with AsyncSessionLocal() as session:
            vs = VectorStore()
            gs = GraphStore(session)
            manager = MemoryManager(vs, gs)
            
            user_prompt = state['messages'][0].content
            memory_context = await manager.recall(state["workspace_id"], user_prompt)
    except Exception as e:
        logger.error("memory_recall_error_in_planner", error=str(e))
        memory_context = "Could not retrieve past memory."
    
    system_prompt = f"{PLANNER_SYSTEM_PROMPT}\n\nContext:\n{memory_context}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Create a step-by-step plan for the following request. Return ONLY JSON.\n\n{state['messages'][0].content}"}
    ]
    
    try:
        response = await router.acompletion(model_type="reasoning", messages=messages, response_format={"type": "json_object"})
        content = response.choices[0].message.content
        
        try:
            data = json.loads(content)
            plan = data.get("steps", data) if isinstance(data, dict) else data
            if not isinstance(plan, list):
                raise ValueError("Parsed plan is not a list")
                
            logger.info("node_plan_success", steps=len(plan))
            return {"plan": plan, "current_step": 0, "is_complete": False}
        except json.JSONDecodeError:
            logger.error("node_plan_parse_error", content=content)
            return {"plan": [{"id": "step_1", "description": state['messages'][0].content, "dependencies": []}], "current_step": 0}

    except Exception as e:
        logger.error("node_plan_error", error=str(e))
        raise
