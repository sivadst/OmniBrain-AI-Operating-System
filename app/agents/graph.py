import json
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.planner import plan_node
from app.agents.nodes.executor import execute_node
from app.agents.nodes.critic import critic_node
from app.agents.nodes.healer import healer_node
from app.agents.nodes.human_interrupt import human_interrupt_node

# Conditional routing functions
def route_after_executor(state: AgentState):
    if state.get("is_complete", False):
        return END
    # Simplified logic: If tool calls were made that need approval, go to interrupt.
    # Otherwise, go to critique.
    return "critic"

def route_after_critic(state: AgentState):
    critique_str = state.get("critique")
    if not critique_str:
        return "healer"
        
    try:
        critique = json.loads(critique_str)
        if critique.get("score", 0) >= 8:
            # If current step exceeds plan length, done. Else loop back to execute.
            if state["current_step"] >= len(state.get("plan", [])):
                return END
            return "execute"
        else:
            return "healer"
    except json.JSONDecodeError:
        return "healer"

def route_after_healer(state: AgentState):
    # If the healer forced a step advance and we reached the end
    if state["current_step"] >= len(state.get("plan", [])):
        return END
    return "execute"

def route_after_interrupt(state: AgentState):
    if state.get("human_approved", False):
        return "execute"
    return END

def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("planner", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("healer", healer_node)
    workflow.add_node("human_interrupt", human_interrupt_node)
    
    # Define Edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "execute")
    
    workflow.add_conditional_edges(
        "execute",
        route_after_executor,
        {
            "critic": "critic",
            "human_interrupt": "human_interrupt",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "execute": "execute",
            "healer": "healer",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "healer",
        route_after_healer,
        {
            "execute": "execute",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "human_interrupt",
        route_after_interrupt,
        {
            "execute": "execute",
            END: END
        }
    )
    
    return workflow
