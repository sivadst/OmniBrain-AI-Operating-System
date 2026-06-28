import litellm
import structlog
from typing import Any, List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

logger = structlog.get_logger(__name__)

# Ensure litellm uses our custom Ollama URL if configured
import os
os.environ["OLLAMA_API_BASE"] = settings.OLLAMA_BASE_URL

class LLMRouter:
    def __init__(self):
        self.reasoning_model = settings.REASONING_MODEL
        self.coding_model = settings.CODING_MODEL
        self.fast_model = settings.FAST_MODEL

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def acompletion(self, model_type: str, messages: List[Dict[str, str]], **kwargs: Any) -> Any:
        model = self._get_model(model_type)
        logger.info("llm_call_start", model=model, model_type=model_type)
        
        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                **kwargs
            )
            
            usage = response.get("usage", {})
            logger.info(
                "llm_call_success", 
                model=model, 
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0)
            )
            return response
            
        except litellm.exceptions.RateLimitError as e:
            logger.warning("llm_rate_limit", error=str(e), model=model)
            raise
        except Exception as e:
            logger.error("llm_call_error", error=str(e), model=model)
            raise

    def _get_model(self, model_type: str) -> str:
        if model_type == "reasoning":
            return self.reasoning_model
        elif model_type == "coding":
            return self.coding_model
        elif model_type == "fast":
            return self.fast_model
        return self.fast_model

def get_llm_router() -> LLMRouter:
    return LLMRouter()
