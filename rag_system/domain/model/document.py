from dataclasses import dataclass, field
from typing import Any

from rag_system.domain.model.embedding import Embedding


@dataclass
class ChunkMetadata:
    source_document_id: str
    page: int | None = None
    position: int = 0


@dataclass
class Chunk:
    id: str
    content: str
    metadata: ChunkMetadata
    embedding: Embedding | None = None


@dataclass
class Document:
    id: str
    content: str
    metadata: dict[str, Any]
    chunks: list[Chunk] | None = field(default=None)
