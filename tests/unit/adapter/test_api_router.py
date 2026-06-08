from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from rag_system.adapter.inbound.api.router import app
from rag_system.config.container import Container
from rag_system.domain.model.document import ChunkMetadata, Document
from rag_system.domain.model.query import QueryResult, SearchResult


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestAPI:
    def test_health(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @patch.object(Container, "query_service")
    def test_query_endpoint(self, mock_service: AsyncMock, client: TestClient) -> None:
        meta = ChunkMetadata(source_document_id="doc-1", position=0)
        mock_service.query = AsyncMock(
            return_value=QueryResult(
                query="hello",
                answer="world",
                results=[
                    SearchResult(chunk_id="c1", content="test content", score=0.95, metadata=meta)
                ],
            )
        )

        response = client.post("/query", json={"text": "hello", "top_k": 5})

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "world"
        assert len(data["results"]) == 1

    def test_query_missing_text(self, client: TestClient) -> None:
        response = client.post("/query", json={})
        assert response.status_code == 422

    @patch.object(Container, "ingestion_service")
    def test_ingest_endpoint(self, mock_service: AsyncMock, client: TestClient) -> None:
        mock_service.ingest = AsyncMock(return_value=None)

        response = client.post(
            "/ingest",
            json={"document_id": "doc-1", "content": "hello world", "metadata": {"source": "test"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["document_id"] == "doc-1"

    @patch.object(Container, "document_store")
    def test_list_documents(self, mock_store: AsyncMock, client: TestClient) -> None:
        mock_store.list = AsyncMock(
            return_value=[
                Document(
                    id="doc-1",
                    content="",
                    metadata={"filename": "doc-1.txt", "_chunk_count": 3},
                    chunks=None,
                ),
                Document(
                    id="doc-2",
                    content="",
                    metadata={"filename": "doc-2.txt", "_chunk_count": 1},
                    chunks=None,
                ),
            ],
        )

        response = client.get("/documents")

        assert response.status_code == 200
        data = response.json()
        assert len(data["documents"]) == 2
        assert data["documents"][0]["id"] == "doc-1"
        assert data["documents"][0]["chunk_count"] == 3
        assert data["documents"][1]["id"] == "doc-2"
        assert data["documents"][1]["chunk_count"] == 1
        assert data["limit"] == 50
        assert data["offset"] == 0

    @patch.object(Container, "document_store")
    def test_get_document_found(self, mock_store: AsyncMock, client: TestClient) -> None:
        doc = Document(id="doc-1", content="hello world", metadata={"filename": "doc-1.txt"})
        mock_store.get = AsyncMock(return_value=doc)

        response = client.get("/documents/doc-1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "doc-1"
        assert data["content"] == "hello world"
        assert data["metadata"] == {"filename": "doc-1.txt"}

    @patch.object(Container, "document_store")
    def test_get_document_not_found(self, mock_store: AsyncMock, client: TestClient) -> None:
        mock_store.get = AsyncMock(return_value=None)

        response = client.get("/documents/nonexistent")

        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found"

    @patch.object(Container, "retriever")
    @patch.object(Container, "document_store")
    def test_delete_document(
        self, mock_store: AsyncMock, mock_retriever: AsyncMock, client: TestClient
    ) -> None:
        doc = Document(id="doc-1", content="hello", metadata={})
        mock_store.get = AsyncMock(return_value=doc)
        mock_store.delete = AsyncMock(return_value=None)
        mock_retriever.delete_chunks = AsyncMock(return_value=None)

        response = client.delete("/documents/doc-1")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"
        assert data["document_id"] == "doc-1"
        mock_retriever.delete_chunks.assert_awaited_once_with("doc-1")

    @patch.object(Container, "document_store")
    def test_delete_document_not_found(self, mock_store: AsyncMock, client: TestClient) -> None:
        mock_store.get = AsyncMock(return_value=None)

        response = client.delete("/documents/nonexistent")

        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found"
