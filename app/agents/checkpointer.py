from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL)

async def get_checkpointer() -> AsyncPostgresSaver:
    """Returns an initialized AsyncPostgresSaver for LangGraph state persistence."""
    checkpointer = AsyncPostgresSaver(engine)
    await checkpointer.setup()
    return checkpointer
