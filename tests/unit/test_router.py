import pytest
from unittest.mock import AsyncMock, patch
from app.llm.router import LLMRouter

@pytest.mark.asyncio
async def test_llm_router_routing():
    router = LLMRouter()
    
    with patch('litellm.acompletion', new_callable=AsyncMock) as mock_acompletion:
        mock_acompletion.return_value = {"choices": [{"message": {"content": "test"}}], "usage": {}}
        
        await router.acompletion("reasoning", [{"role": "user", "content": "hi"}])
        
        # Verify it routes to the correct model name defined in settings
        mock_acompletion.assert_called_once()
        args, kwargs = mock_acompletion.call_args
        assert kwargs["model"] == router.reasoning_model
