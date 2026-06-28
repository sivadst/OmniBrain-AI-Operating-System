class OmniBrainException(Exception):
    """Base exception for OmniBrain"""
    pass

class AgentExecutionError(OmniBrainException):
    """Raised when an agent execution fails"""
    pass

class ToolExecutionError(OmniBrainException):
    """Raised when a tool execution fails"""
    pass

class MemoryRetrievalError(OmniBrainException):
    """Raised when memory retrieval fails"""
    pass

class HumanInterruptRequired(OmniBrainException):
    """Raised when a process requires human intervention"""
    pass
