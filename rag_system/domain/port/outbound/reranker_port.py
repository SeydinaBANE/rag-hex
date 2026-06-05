from abc import ABC, abstractmethod

from rag_system.domain.model.query import SearchResult


class RerankerPort(ABC):
    @abstractmethod
    async def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]: ...
