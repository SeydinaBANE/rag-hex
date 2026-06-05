from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from rag_system.adapter.inbound.api.router import app
from rag_system.config.container import Container
from rag_system.domain.model.document import ChunkMetadata
from rag_system.domain.model.query import QueryResult, SearchResult


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestAPI:
    def test_health(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

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
