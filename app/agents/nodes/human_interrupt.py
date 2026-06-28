import structlog
from typing import Dict, Any
from langgraph.types import interrupt
from app.agents.state import AgentState

logger = structlog.get_logger(__name__)

async def human_interrupt_node(state: AgentState) -> Dict[str, Any]:
    """Pauses the graph execution for human approval."""
    logger.info("node_human_interrupt")
    
    # Standard LangGraph pause
    user_approval = interrupt("Task requires human approval to proceed.")
    
    return {"human_approved": user_approval == "approve"}
