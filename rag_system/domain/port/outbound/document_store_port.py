from abc import ABC, abstractmethod

from rag_system.domain.model.document import Document


class DocumentStorePort(ABC):
    @abstractmethod
    async def store(self, document: Document) -> None: ...

    @abstractmethod
    async def get(self, document_id: str) -> Document | None: ...

    @abstractmethod
    async def delete(self, document_id: str) -> None: ...

    @abstractmethod
    async def list(self, limit: int = 50, offset: int = 0) -> list[Document]: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    @abstractmethod
    async def close(self) -> None: ...
