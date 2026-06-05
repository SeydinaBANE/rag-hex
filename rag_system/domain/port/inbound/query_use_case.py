from abc import ABC, abstractmethod

from rag_system.domain.model.query import Query, QueryResult


class QueryUseCase(ABC):
    @abstractmethod
    async def query(self, query: Query) -> QueryResult: ...
