from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db_session
from app.core.config import settings
from app.db.models import Workspace

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_workspace(
    api_key_header: str = Security(api_key_header),
    session: AsyncSession = Depends(get_db_session)
) -> str:
    """
    Validates the API Key and returns the associated workspace_id.
    """
    if api_key_header == settings.API_KEY:
        # For simplicity in this demo, return a default workspace ID if API key matches the dev key.
        # But let's actually ensure it exists in the DB.
        stmt = select(Workspace).where(Workspace.name == "default_workspace")
        result = await session.execute(stmt)
        workspace = result.scalar_one_or_none()
        if not workspace:
            workspace = Workspace(name="default_workspace")
            session.add(workspace)
            await session.commit()
            await session.refresh(workspace)
        return workspace.id
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )
