from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMPort(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: list[str]) -> str: ...

    @abstractmethod
    def generate_stream(self, prompt: str, context: list[str]) -> AsyncIterator[str]: ...

    @abstractmethod
    async def close(self) -> None: ...
