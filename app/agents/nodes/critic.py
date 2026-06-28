import json
import structlog
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.llm.router import get_llm_router
from app.llm.prompts import CRITIC_SYSTEM_PROMPT
from app.agents.state import AgentState

logger = structlog.get_logger(__name__)

async def critic_node(state: AgentState) -> Dict[str, Any]:
    """Evaluates the execution of the current step."""
    logger.info("node_critic_start")
    
    router = get_llm_router()
    
    # Get last execution outputs
    last_actions = "\n".join([msg.content for msg in state["messages"][-3:] if isinstance(msg, AIMessage) or msg.type == 'tool'])
    current_step = state["plan"][state["current_step"]]
    
    messages = [
        {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
        {"role": "user", "content": f"Task: {current_step['description']}\n\nExecution Log:\n{last_actions}\n\nEvaluate and return JSON."}
    ]
    
    try:
        response = await router.acompletion(model_type="reasoning", messages=messages, response_format={"type": "json_object"})
        content = response.choices[0].message.content
        
        try:
            data = json.loads(content)
            score = data.get("score", 0)
            feedback = data.get("feedback")
            
            critique = json.dumps({"score": score, "feedback": feedback})
            logger.info("node_critic_success", score=score)
            
            if score >= 8:
                return {"critique": critique, "current_step": state["current_step"] + 1}
            else:
                return {"critique": critique}
                
        except json.JSONDecodeError:
            return {"critique": json.dumps({"score": 5, "feedback": "Failed to parse critique JSON."})}

    except Exception as e:
        logger.error("node_critic_error", error=str(e))
        return {"critique": json.dumps({"score": 1, "feedback": f"Critic error: {str(e)}"}) }
