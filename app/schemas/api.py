from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class TaskCreateRequest(BaseModel):
    prompt: str = Field(..., description="The main prompt or task description for the agent")
    workspace_id: str = Field(..., description="The ID of the workspace this task belongs to")

class TaskResponse(BaseModel):
    id: str
    status: str
    created_at: datetime
    final_output: Optional[str] = None

class StreamEvent(BaseModel):
    event_type: str
    data: Dict[str, Any]
