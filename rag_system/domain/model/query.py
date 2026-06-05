from dataclasses import dataclass, field
from typing import Any

from rag_system.domain.model.document import ChunkMetadata


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    content: str
    score: float
    metadata: ChunkMetadata


@dataclass
class QueryResult:
    query: str
    results: list[SearchResult] = field(default_factory=list)
    answer: str | None = None


@dataclass(frozen=True)
class Query:
    text: str
    top_k: int = 5
    filters: dict[str, Any] | None = None
