import heapq

from rag_system.domain.model.document import Chunk, ChunkMetadata
from rag_system.domain.model.embedding import Embedding
from rag_system.domain.model.query import Query, SearchResult
from rag_system.domain.port.outbound.retriever_port import RetrieverPort


class InMemoryRetriever(RetrieverPort):
    def __init__(self) -> None:
        self._chunks: list[tuple[str, str, ChunkMetadata]] = []

    async def store_chunks(self, chunks: list[Chunk]) -> None:
        for c in chunks:
            self._chunks.append((c.id, c.content, c.metadata))

    def clear(self) -> None:
        self._chunks.clear()

    async def search(self, query: Query, query_embedding: Embedding) -> list[SearchResult]:
        _ = query_embedding
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

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        self.clear()

    def _simple_score(self, query: str, content: str) -> float:
        q_lower = query.lower()
        c_lower = content.lower()
        words = q_lower.split()
        if not words:
            return 0.0
        matches = sum(1 for w in words if w in c_lower)
        return matches / len(words)
