from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from rag_system.domain.model.query import Query, QueryResult


class QueryUseCase(ABC):
    @abstractmethod
    async def query(self, query: Query) -> QueryResult: ...

    @abstractmethod
    def query_stream(self, query: Query) -> AsyncIterator[str]: ...
