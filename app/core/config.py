from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App config
    PROJECT_NAME: str = "OmniBrain API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Auth
    API_KEY: str = "development_key"

    # Infrastructure URLs
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/omnibrain"
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_URL: str = "http://localhost:6333"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Model Routing
    REASONING_MODEL: str = "ollama/llama3"
    CODING_MODEL: str = "ollama/llama3"
    FAST_MODEL: str = "ollama/llama3"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
