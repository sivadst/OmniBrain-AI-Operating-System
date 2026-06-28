from fastapi import APIRouter
from app.api.endpoints import tasks, memory, ws

api_router = APIRouter()

api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(ws.router, prefix="/stream", tags=["streaming"])
