from collections.abc import AsyncIterator

import httpx
import pytest

API_URL = "http://localhost:8000"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=API_URL, timeout=30.0) as c:
        yield c


class TestHealth:
    async def test_health(self, client: httpx.AsyncClient) -> None:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestIngest:
    async def test_ingest_document(self, client: httpx.AsyncClient) -> None:
        resp = await client.post(
            "/ingest",
            json={
                "document_id": "integration-test-doc",
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
        assert data["document_id"] == "integration-test-doc"

    async def test_ingest_missing_fields(self, client: httpx.AsyncClient) -> None:
        resp = await client.post("/ingest", json={})
        assert resp.status_code == 422


class TestQuery:
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
