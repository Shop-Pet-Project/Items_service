from abc import ABC, abstractmethod
from typing import Any


class BaseSerializer(ABC):
    @abstractmethod
    def dumps(self, data: Any) -> str:
        pass

    @abstractmethod
    def loads(self, data: str) -> Any:
        pass
