import pytest
from app.agents.graph import build_graph
from langgraph.graph import StateGraph

def test_graph_compilation():
    """Ensures the graph builds and compiles without syntax/routing errors."""
    workflow = build_graph()
    assert isinstance(workflow, StateGraph)
    
    # We can compile it without a checkpointer to verify standard structure
    compiled = workflow.compile()
    assert compiled is not None
