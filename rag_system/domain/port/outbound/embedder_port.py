from abc import ABC, abstractmethod

from rag_system.domain.model.embedding import Embedding


class EmbedderPort(ABC):
    @abstractmethod
    async def embed(self, text: str) -> Embedding:
        ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[Embedding]:
        ...
