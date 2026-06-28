from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import Workspace, Task, AgentTrace, GraphNode, GraphEdge
import uuid

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, workspace_id: str, prompt: str) -> Task:
        task = Task(workspace_id=workspace_id, prompt=prompt, status="PENDING")
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def update_task_status(self, task_id: str, status: str, final_output: Optional[str] = None) -> Optional[Task]:
        values: Dict[str, Any] = {"status": status}
        if final_output is not None:
            values["final_output"] = final_output
        stmt = update(Task).where(Task.id == task_id).values(**values).returning(Task)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

class AgentTraceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_trace(self, task_id: str, node_name: str, input_state: dict, output_state: dict, 
                         tokens_used: int = 0, cost_usd: float = 0.0, latency_ms: float = 0.0) -> AgentTrace:
        trace = AgentTrace(
            task_id=task_id,
            node_name=node_name,
            input_state=input_state,
            output_state=output_state,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            latency_ms=latency_ms
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace

class GraphRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_node(self, node_id: str, workspace_id: str, node_type: str, properties: dict) -> GraphNode:
        node = GraphNode(id=node_id, workspace_id=workspace_id, type=node_type, properties=properties)
        self.session.add(node)
        await self.session.commit()
        await self.session.refresh(node)
        return node

    async def add_edge(self, source_id: str, target_id: str, workspace_id: str, relationship_type: str, properties: dict) -> GraphEdge:
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            workspace_id=workspace_id,
            relationship_type=relationship_type,
            properties=properties
        )
        self.session.add(edge)
        await self.session.commit()
        await self.session.refresh(edge)
        return edge

    async def get_node(self, node_id: str, workspace_id: str) -> Optional[GraphNode]:
        result = await self.session.execute(
            select(GraphNode).where(GraphNode.id == node_id, GraphNode.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()
