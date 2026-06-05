from abc import ABC, abstractmethod

from rag_system.domain.model.query import Query, SearchResult


class RetrieverPort(ABC):
    @abstractmethod
    async def search(self, query: Query) -> list[SearchResult]:
        ...
