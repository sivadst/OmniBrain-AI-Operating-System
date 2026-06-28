from typing import Dict, Any, List
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]

class KnowledgeNode(BaseModel):
    id: str
    type: str
    properties: Dict[str, Any]
