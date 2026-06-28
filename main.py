import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
import structlog
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.router import api_router
from app.core.database import engine, redis_pool
from app.memory.vector_store import VectorStore
# Initialize opentelemetry early if needed here, but usually done via middleware.

setup_logging(settings.LOG_LEVEL)
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup")
    
    # Init Vector Store
    vs = VectorStore()
    await vs.initialize()
    
    yield
    
    logger.info("application_shutdown")
    await engine.dispose()
    await redis_pool.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
