from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rag_system.adapter.outbound.retrieval.qdrant_retriever import QdrantRetriever
from rag_system.domain.model.document import Chunk, ChunkMetadata
from rag_system.domain.model.embedding import Embedding
from rag_system.domain.model.query import Query


@pytest.fixture
def retriever() -> QdrantRetriever:
    with patch("rag_system.adapter.outbound.retrieval.qdrant_retriever.AsyncQdrantClient"):
        return QdrantRetriever(url="http://localhost:6333", collection_name="test")


class TestQdrantRetriever:
    async def test_ping_returns_true_on_success(self, retriever: QdrantRetriever) -> None:
        retriever._client.get_collections = AsyncMock(return_value=MagicMock())

        result = await retriever.ping()

        assert result is True

    async def test_ping_returns_false_on_failure(self, retriever: QdrantRetriever) -> None:
        retriever._client.get_collections = AsyncMock(side_effect=Exception("connection refused"))

        result = await retriever.ping()

        assert result is False

    async def test_store_chunks_skips_when_empty(self, retriever: QdrantRetriever) -> None:
        retriever._client.upsert = AsyncMock()

        await retriever.store_chunks([])

        retriever._client.upsert.assert_not_awaited()

    async def test_store_chunks_skips_when_no_embeddings(self, retriever: QdrantRetriever) -> None:
        retriever._client.upsert = AsyncMock()
        chunks = [
            Chunk(
                id="c1",
                content="hello",
                metadata=ChunkMetadata(source_document_id="doc-1", position=0),
            )
        ]

        await retriever.store_chunks(chunks)

        retriever._client.upsert.assert_not_awaited()

    async def test_store_chunks_upserts_to_qdrant(self, retriever: QdrantRetriever) -> None:
        retriever._client.upsert = AsyncMock()
        retriever._client.create_collection = AsyncMock()
        existing_col = MagicMock()
        existing_col.name = "test"
        retriever._client.get_collections = AsyncMock(
            return_value=MagicMock(collections=[existing_col])
        )
        chunk = Chunk(
            id="doc-1__chunk_0",
            content="hello world",
            metadata=ChunkMetadata(source_document_id="doc-1", position=0),
            embedding=Embedding(vector=[0.1, 0.2], model="test", dimensions=2),
        )

        await retriever.store_chunks([chunk])

        retriever._client.upsert.assert_awaited_once()
        call_kwargs = retriever._client.upsert.call_args.kwargs
        assert call_kwargs["collection_name"] == "test"
        assert len(call_kwargs["points"]) == 1

    async def test_search_returns_empty_on_no_results(self, retriever: QdrantRetriever) -> None:
        mock_response = MagicMock()
        mock_response.points = []
        retriever._client.query_points = AsyncMock(return_value=mock_response)

        embedding = Embedding(vector=[0.1, 0.2], model="test", dimensions=2)
        results = await retriever.search(Query(text="hello", top_k=5), embedding)

        assert results == []

    async def test_delete_chunks_calls_qdrant_delete(self, retriever: QdrantRetriever) -> None:
        existing_col = MagicMock()
        existing_col.name = "test"
        retriever._client.get_collections = AsyncMock(
            return_value=MagicMock(collections=[existing_col])
        )
        retriever._client.delete = AsyncMock()

        await retriever.delete_chunks("doc-1")

        retriever._client.delete.assert_awaited_once()
        call_kwargs = retriever._client.delete.call_args.kwargs
        assert call_kwargs["collection_name"] == "test"

    async def test_delete_chunks_skips_when_collection_not_exists(
        self, retriever: QdrantRetriever
    ) -> None:
        retriever._client.get_collections = AsyncMock(return_value=MagicMock(collections=[]))
        retriever._client.delete = AsyncMock()

        await retriever.delete_chunks("doc-1")

        retriever._client.delete.assert_not_awaited()

    async def test_search_maps_points_to_results(self, retriever: QdrantRetriever) -> None:
        point = MagicMock()
        point.score = 0.9
        point.payload = {
            "chunk_id": "doc-1__chunk_0",
            "content": "hello world",
            "source_document_id": "doc-1",
            "position": 0,
        }
        mock_response = MagicMock()
        mock_response.points = [point]
        retriever._client.query_points = AsyncMock(return_value=mock_response)

        embedding = Embedding(vector=[0.1, 0.2], model="test", dimensions=2)
        results = await retriever.search(Query(text="hello", top_k=5), embedding)

        assert len(results) == 1
        assert results[0].chunk_id == "doc-1__chunk_0"
        assert results[0].content == "hello world"
        assert results[0].score == 0.9
