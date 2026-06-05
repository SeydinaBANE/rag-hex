import httpx

from rag_system.domain.model.query import SearchResult
from rag_system.domain.port.outbound.reranker_port import RerankerPort


class CohereReranker(RerankerPort):
    def __init__(self, api_key: str, model: str = "rerank-multilingual-v3.0") -> None:
        self._model = model
        self._client = httpx.AsyncClient(
            base_url="https://api.cohere.com/v1",
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        response = await self._client.post(
            "/rerank",
            json={
                "model": self._model,
                "query": query,
                "documents": [r.content for r in results],
                "top_n": len(results),
            },
        )
        response.raise_for_status()
        data = response.json()

        reranked: list[SearchResult] = []
        for item in data["results"]:
            idx = item["index"]
            original = results[idx]
            reranked.append(
                SearchResult(
                    chunk_id=original.chunk_id,
                    content=original.content,
                    score=item["relevance_score"],
                    metadata=original.metadata,
                )
            )

        return reranked

    async def close(self) -> None:
        await self._client.aclose()
