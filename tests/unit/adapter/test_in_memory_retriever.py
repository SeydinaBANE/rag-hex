import pytest

from rag_system.adapter.outbound.retrieval.in_memory_retriever import InMemoryRetriever
from rag_system.domain.model.document import ChunkMetadata
from rag_system.domain.model.query import Query


class TestInMemoryRetriever:
    @pytest.fixture
    def retriever(self) -> InMemoryRetriever:
        return InMemoryRetriever()

    async def test_search_empty_returns_empty_list(self, retriever: InMemoryRetriever) -> None:
        results = await retriever.search(Query(text="hello"))
        assert results == []

    async def test_search_finds_matching_chunks(self, retriever: InMemoryRetriever) -> None:
        retriever.add_chunk(
            "chunk-1",
            "Le chat mange une souris",
            ChunkMetadata(source_document_id="doc-1", position=0),
        )
        retriever.add_chunk(
            "chunk-2",
            "Le chien court dans le parc",
            ChunkMetadata(source_document_id="doc-1", position=1),
        )

        results = await retriever.search(Query(text="chat souris", top_k=5))

        assert len(results) == 2
        assert results[0].chunk_id == "chunk-1"
        assert results[0].score > 0

    async def test_search_respects_top_k(self, retriever: InMemoryRetriever) -> None:
        for i in range(5):
            retriever.add_chunk(
                f"chunk-{i}",
                f"contenu avec le mot chat numero {i}",
                ChunkMetadata(source_document_id="doc-1", position=i),
            )

        results = await retriever.search(Query(text="chat", top_k=3))
        assert len(results) == 3

    async def test_clear_removes_all_chunks(self, retriever: InMemoryRetriever) -> None:
        retriever.add_chunk(
            "chunk-1", "test", ChunkMetadata(source_document_id="doc-1", position=0)
        )
        retriever.clear()
        results = await retriever.search(Query(text="test"))
        assert results == []
