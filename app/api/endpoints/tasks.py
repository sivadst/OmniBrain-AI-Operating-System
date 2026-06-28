from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from arq import create_pool
from arq.connections import RedisSettings
from app.core.database import get_db_session
from app.core.config import settings
from app.api.deps import get_current_workspace
from app.db.repositories import TaskRepository
from app.schemas.api import TaskCreateRequest, TaskResponse

router = APIRouter()

async def get_arq_pool():
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    return await create_pool(redis_settings)

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreateRequest,
    workspace_id: str = Depends(get_current_workspace),
    session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    task = await repo.create_task(workspace_id, request.prompt)
    
    # Push to ARQ
    try:
        pool = await get_arq_pool()
        await pool.enqueue_job('execute_agent_task', task.id, request.prompt, workspace_id)
        await pool.close()
    except Exception as e:
        await repo.update_task_status(task.id, "FAILED", f"Failed to enqueue: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to enqueue task")
        
    return TaskResponse(
        id=task.id,
        status=task.status,
        created_at=task.created_at
    )

@router.post("/{task_id}/resume", response_model=TaskResponse)
async def resume_task(
    task_id: str,
    action: str, # "approve" or "reject"
    workspace_id: str = Depends(get_current_workspace),
    session: AsyncSession = Depends(get_db_session)
):
    repo = TaskRepository(session)
    task = await repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status != "INTERRUPTED":
        raise HTTPException(status_code=400, detail="Task is not interrupted")
        
    # Push resume command to ARQ
    pool = await get_arq_pool()
    await pool.enqueue_job('resume_agent_task', task.id, action)
    await pool.close()
    
    task = await repo.update_task_status(task.id, "RUNNING")
    
    return TaskResponse(
        id=task.id,
        status=task.status,
        created_at=task.created_at
    )
