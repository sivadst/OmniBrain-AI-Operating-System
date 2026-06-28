import structlog
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.llm.router import get_llm_router
from app.llm.prompts import HEALER_SYSTEM_PROMPT
from app.agents.state import AgentState

logger = structlog.get_logger(__name__)

async def healer_node(state: AgentState) -> Dict[str, Any]:
    """Self-corrects based on critic feedback or tool errors."""
    logger.info("node_healer_start")
    
    router = get_llm_router()
    
    messages = [
        {"role": "system", "content": HEALER_SYSTEM_PROMPT},
        {"role": "user", "content": f"The previous execution failed or received low critique.\nCritique: {state['critique']}\nAnalyze and provide a revised plan of action for the executor."}
    ]
    
    try:
        response = await router.acompletion(model_type="reasoning", messages=messages)
        correction = response.choices[0].message.content
        
        logger.info("node_healer_success")
        return {"messages": [AIMessage(content=f"[Self-Healing Correction] {correction}")]}
    except Exception as e:
        logger.error("node_healer_error", error=str(e))
        return {"messages": [AIMessage(content="Healing failed. Forcing next step to avoid infinite loop.")], "current_step": state["current_step"] + 1}
