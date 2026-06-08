import pytest

from rag_system.adapter.outbound.retrieval.in_memory_retriever import InMemoryRetriever
from rag_system.domain.model.document import Chunk, ChunkMetadata
from rag_system.domain.model.embedding import Embedding
from rag_system.domain.model.query import Query


@pytest.fixture
def query_embedding() -> Embedding:
    return Embedding(vector=[0.0], model="test", dimensions=1)


class TestInMemoryRetriever:
    @pytest.fixture
    def retriever(self) -> InMemoryRetriever:
        return InMemoryRetriever()

    async def test_search_empty_returns_empty_list(
        self, retriever: InMemoryRetriever, query_embedding: Embedding
    ) -> None:
        results = await retriever.search(Query(text="hello"), query_embedding)
        assert results == []

    async def test_search_finds_matching_chunks(
        self, retriever: InMemoryRetriever, query_embedding: Embedding
    ) -> None:
        await retriever.store_chunks(
            [
                Chunk(
                    id="chunk-1",
                    content="Le chat mange une souris",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=0),
                ),
                Chunk(
                    id="chunk-2",
                    content="Le chien court dans le parc",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=1),
                ),
            ]
        )

        results = await retriever.search(Query(text="chat souris", top_k=5), query_embedding)

        assert len(results) == 2
        assert results[0].chunk_id == "chunk-1"
        assert results[0].score > 0

    async def test_search_respects_top_k(
        self, retriever: InMemoryRetriever, query_embedding: Embedding
    ) -> None:
        await retriever.store_chunks(
            [
                Chunk(
                    id=f"chunk-{i}",
                    content=f"contenu avec le mot chat numero {i}",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=i),
                )
                for i in range(5)
            ]
        )

        results = await retriever.search(Query(text="chat", top_k=3), query_embedding)
        assert len(results) == 3

    async def test_clear_removes_all_chunks(
        self, retriever: InMemoryRetriever, query_embedding: Embedding
    ) -> None:
        await retriever.store_chunks(
            [
                Chunk(
                    id="chunk-1",
                    content="test",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=0),
                ),
            ]
        )
        retriever.clear()
        results = await retriever.search(Query(text="test"), query_embedding)
        assert results == []

    async def test_delete_chunks_removes_only_target_document(
        self, retriever: InMemoryRetriever, query_embedding: Embedding
    ) -> None:
        await retriever.store_chunks(
            [
                Chunk(
                    id="chunk-1",
                    content="doc one content",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=0),
                ),
                Chunk(
                    id="chunk-2",
                    content="doc two content",
                    metadata=ChunkMetadata(source_document_id="doc-2", position=0),
                ),
            ]
        )

        await retriever.delete_chunks("doc-1")

        results = await retriever.search(Query(text="doc content"), query_embedding)
        assert all(r.metadata.source_document_id != "doc-1" for r in results)
        assert any(r.metadata.source_document_id == "doc-2" for r in results)

    async def test_delete_chunks_noop_when_document_not_present(
        self, retriever: InMemoryRetriever, query_embedding: Embedding
    ) -> None:
        await retriever.store_chunks(
            [
                Chunk(
                    id="chunk-1",
                    content="some content",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=0),
                ),
            ]
        )

        await retriever.delete_chunks("doc-nonexistent")

        results = await retriever.search(Query(text="some"), query_embedding)
        assert len(results) == 1
