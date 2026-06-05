from abc import ABC, abstractmethod

from rag_system.domain.model.document import Document


class IngestionUseCase(ABC):
    @abstractmethod
    async def ingest(self, document: Document) -> None: ...
