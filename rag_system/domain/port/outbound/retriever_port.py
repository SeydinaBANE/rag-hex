from abc import ABC, abstractmethod

from rag_system.domain.model.document import Chunk
from rag_system.domain.model.embedding import Embedding
from rag_system.domain.model.query import Query, SearchResult


class RetrieverPort(ABC):
    @abstractmethod
    async def search(self, query: Query, query_embedding: Embedding) -> list[SearchResult]: ...

    @abstractmethod
    async def store_chunks(self, chunks: list[Chunk]) -> None: ...

    @abstractmethod
    async def delete_chunks(self, document_id: str) -> None: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    @abstractmethod
    async def close(self) -> None: ...
