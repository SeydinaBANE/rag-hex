from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from rag_system.domain.model.embedding import Embedding
from rag_system.domain.model.query import Query, SearchResult
from rag_system.domain.port.outbound.retriever_port import RetrieverPort


class QdrantRetriever(RetrieverPort):
    def __init__(self, url: str, collection_name: str = "rag_documents") -> None:
        self._client = AsyncQdrantClient(url=url)
        self._collection_name = collection_name

    async def ensure_collection(self, vector_size: int) -> None:
        collections = await self._client.get_collections()
        exists = any(c.name == self._collection_name for c in collections.collections)
        if not exists:
            await self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    async def upsert_chunk(
        self, chunk_id: str, embedding: Embedding, payload: dict[str, Any]
    ) -> None:
        await self._client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(
                    id=hash(chunk_id),
                    vector=embedding.vector,
                    payload=payload,
                )
            ],
        )

    async def search(self, query: Query) -> list[SearchResult]:
        _ = query
        return []

    async def close(self) -> None:
        await self._client.close()
