from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.api.deps import get_current_workspace
from app.memory.manager import MemoryManager
from app.memory.vector_store import VectorStore
from app.memory.graph_store import GraphStore
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session

router = APIRouter()

async def get_memory_manager(session: AsyncSession = Depends(get_db_session)) -> MemoryManager:
    vs = VectorStore()
    gs = GraphStore(session)
    return MemoryManager(vs, gs)

@router.get("/recall")
async def recall_memory(
    query: str,
    workspace_id: str = Depends(get_current_workspace),
    manager: MemoryManager = Depends(get_memory_manager)
):
    """Retrieve episodic and semantic memory context based on a query."""
    context = await manager.recall(workspace_id, query)
    return {"context": context}
