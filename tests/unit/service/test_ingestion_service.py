from unittest.mock import AsyncMock

import pytest

from rag_system.domain.model.document import Chunk, Document
from rag_system.domain.model.embedding import Embedding
from rag_system.domain.service.ingestion_service import IngestionService


class TestIngestionService:
    @pytest.fixture
    def mock_ports(self) -> tuple[AsyncMock, AsyncMock, AsyncMock]:
        return AsyncMock(), AsyncMock(), AsyncMock()

    @pytest.fixture
    def service(self, mock_ports: tuple[AsyncMock, AsyncMock, AsyncMock]) -> IngestionService:
        embedder, doc_store, retriever = mock_ports
        return IngestionService(
            embedder=embedder,
            document_store=doc_store,
            retriever=retriever,
            chunk_size=10,
            chunk_overlap=2,
        )

    async def test_ingest_document(
        self, service: IngestionService, mock_ports: tuple[AsyncMock, AsyncMock, AsyncMock]
    ) -> None:
        embedder, doc_store, retriever = mock_ports
        doc = Document(id="doc-1", content="Hello world this is a test document", metadata={})

        chunks = service._chunk_document(doc)
        mock_embeddings = [Embedding(vector=[0.1, 0.2], model="test", dimensions=2) for _ in chunks]
        embedder.embed_batch = AsyncMock(return_value=mock_embeddings)

        await service.ingest(doc)

        embedder.embed_batch.assert_awaited_once()
        doc_store.store.assert_awaited_once()
        retriever.store_chunks.assert_awaited_once()

        assert doc.chunks is not None
        assert len(doc.chunks) > 0
        for chunk in doc.chunks:
            assert chunk.embedding is not None

    async def test_ingest_empty_document(
        self, service: IngestionService, mock_ports: tuple[AsyncMock, AsyncMock, AsyncMock]
    ) -> None:
        embedder, doc_store, retriever = mock_ports
        doc = Document(id="doc-1", content="", metadata={})

        embedder.embed_batch = AsyncMock(return_value=[])

        await service.ingest(doc)

        doc_store.store.assert_awaited_once()
        retriever.store_chunks.assert_awaited_once()
        assert doc.chunks is not None
        assert len(doc.chunks) == 0

    def test_chunk_document(self, service: IngestionService) -> None:
        doc = Document(id="doc-1", content="Hello world this is a test", metadata={})
        chunks = service._chunk_document(doc)

        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)
        assert chunks[0].metadata.source_document_id == "doc-1"
