import operator
from typing import Annotated, TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    plan: list[dict]
    current_step: int
    tool_calls: list[dict]
    critique: Optional[str]
    is_complete: bool
    human_approved: bool
    workspace_id: str
