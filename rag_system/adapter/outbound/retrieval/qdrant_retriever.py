import hashlib
import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from rag_system.domain.model.document import Chunk, ChunkMetadata
from rag_system.domain.model.embedding import Embedding
from rag_system.domain.model.query import Query, SearchResult
from rag_system.domain.port.outbound.retriever_port import RetrieverPort

logger = logging.getLogger(__name__)


def _stable_id(chunk_id: str) -> int:
    return int(hashlib.md5(chunk_id.encode(), usedforsecurity=False).hexdigest()[:15], 16)


class QdrantRetriever(RetrieverPort):
    def __init__(
        self,
        url: str,
        collection_name: str = "rag_documents",
        timeout: int = 10,
    ) -> None:
        self._client = AsyncQdrantClient(url=url, timeout=timeout)
        self._collection_name = collection_name

    async def ping(self) -> bool:
        try:
            await self._client.get_collections()
            return True
        except Exception:
            logger.warning("Qdrant ping failed")
            return False

    async def store_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        first = next((c for c in chunks if c.embedding is not None), None)
        if first is None or first.embedding is None:
            return

        await self._ensure_collection(first.embedding.dimensions)

        points = [
            PointStruct(
                id=_stable_id(c.id),
                vector=c.embedding.vector if c.embedding else [],
                payload={
                    "chunk_id": c.id,
                    "content": c.content,
                    "source_document_id": c.metadata.source_document_id,
                    "position": c.metadata.position,
                },
            )
            for c in chunks
            if c.embedding is not None
        ]

        await self._client.upsert(
            collection_name=self._collection_name,
            points=points,
        )

    async def _ensure_collection(self, vector_size: int) -> None:
        collections = await self._client.get_collections()
        exists = any(c.name == self._collection_name for c in collections.collections)
        if not exists:
            await self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    async def search(self, query: Query, query_embedding: Embedding) -> list[SearchResult]:
        response = await self._client.query_points(
            collection_name=self._collection_name,
            query=query_embedding.vector,
            limit=query.top_k,
        )

        results: list[SearchResult] = []
        for point in response.points:
            payload = point.payload or {}

            results.append(
                SearchResult(
                    chunk_id=payload.get("chunk_id", ""),
                    content=payload.get("content", ""),
                    score=point.score,
                    metadata=ChunkMetadata(
                        source_document_id=payload.get("source_document_id", ""),
                        position=payload.get("position", 0),
                    ),
                )
            )

        return results

    async def close(self) -> None:
        await self._client.close()
