from collections.abc import AsyncIterator

import httpx
import pytest
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

API_URL = "http://localhost:8000"
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "rag_documents"
_TEST_DOC_ID = "integration-test-doc"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=API_URL, timeout=30.0) as c:
        yield c


async def _purge_test_vectors() -> None:
    qdrant = AsyncQdrantClient(url=QDRANT_URL)
    try:
        await qdrant.delete(
            collection_name=QDRANT_COLLECTION,
            points_selector=Filter(
                must=[
                    FieldCondition(key="source_document_id", match=MatchValue(value=_TEST_DOC_ID))
                ]  # noqa: E501
            ),
        )
    except Exception:
        pass
    finally:
        await qdrant.close()


class TestHealth:
    async def test_health(self, client: httpx.AsyncClient) -> None:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestIngest:
    @pytest.fixture(autouse=True)
    async def cleanup(self, client: httpx.AsyncClient) -> AsyncIterator[None]:
        yield
        await client.delete(f"/documents/{_TEST_DOC_ID}")
        await _purge_test_vectors()

    async def test_ingest_document(self, client: httpx.AsyncClient) -> None:
        resp = await client.post(
            "/ingest",
            json={
                "document_id": _TEST_DOC_ID,
                "content": (
                    "PostgreSQL is a powerful open source object-relational database system."
                ),
                "metadata": {"source": "integration-test"},
            },
        )

        if resp.status_code == 500 and "401" in resp.text:
            pytest.skip("OpenRouter API key not configured")

        assert resp.status_code == 200, f"Ingest failed: {resp.text}"
        data = resp.json()
        assert data["status"] == "ok"
        assert data["document_id"] == _TEST_DOC_ID

    async def test_ingest_missing_fields(self, client: httpx.AsyncClient) -> None:
        resp = await client.post("/ingest", json={})
        assert resp.status_code == 422


class TestQuery:
    @pytest.fixture(autouse=True)
    async def ensure_clean_state(self, client: httpx.AsyncClient) -> None:
        await client.delete(f"/documents/{_TEST_DOC_ID}")
        await _purge_test_vectors()

    async def test_query_no_results(self, client: httpx.AsyncClient) -> None:
        resp = await client.post(
            "/query",
            json={"text": "something unlikely to match anything", "top_k": 3},
        )
        assert resp.status_code == 200, f"Query failed: {resp.text}"
        data = resp.json()

        assert data["query"] == "something unlikely to match anything"
        assert data["results"] == []
        assert data["answer"] is None

    async def test_query_stream_no_results(self, client: httpx.AsyncClient) -> None:
        resp = await client.post(
            "/query/stream",
            json={"text": "something unlikely to match anything", "top_k": 3},
        )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")

        lines = [line async for line in resp.aiter_lines() if line.startswith("data: ")]
        assert lines == ["data: [DONE]"]

    async def test_query_missing_text(self, client: httpx.AsyncClient) -> None:
        resp = await client.post("/query", json={})
        assert resp.status_code == 422
