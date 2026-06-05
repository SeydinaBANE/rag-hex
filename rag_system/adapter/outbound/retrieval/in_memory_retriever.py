import heapq

from rag_system.domain.model.document import ChunkMetadata
from rag_system.domain.model.query import Query, SearchResult
from rag_system.domain.port.outbound.retriever_port import RetrieverPort


class InMemoryRetriever(RetrieverPort):
    def __init__(self) -> None:
        self._chunks: list[tuple[str, str, ChunkMetadata]] = []

    def add_chunk(self, chunk_id: str, content: str, metadata: ChunkMetadata) -> None:
        self._chunks.append((chunk_id, content, metadata))

    def clear(self) -> None:
        self._chunks.clear()

    async def search(self, query: Query) -> list[SearchResult]:
        if not self._chunks:
            return []

        scored: list[tuple[float, str, str, ChunkMetadata]] = []
        for chunk_id, content, metadata in self._chunks:
            score = self._simple_score(query.text, content)
            scored.append((score, chunk_id, content, metadata))

        top_k = heapq.nlargest(query.top_k, scored, key=lambda x: x[0])

        return [
            SearchResult(chunk_id=cid, content=content, score=score, metadata=meta)
            for score, cid, content, meta in top_k
        ]

    def _simple_score(self, query: str, content: str) -> float:
        q_lower = query.lower()
        c_lower = content.lower()
        words = q_lower.split()
        if not words:
            return 0.0
        matches = sum(1 for w in words if w in c_lower)
        return matches / len(words)
