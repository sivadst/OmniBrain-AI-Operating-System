from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseInternalTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool's core logic"""
        pass
