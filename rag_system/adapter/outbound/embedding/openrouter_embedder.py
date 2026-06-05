import httpx

from rag_system.domain.model.embedding import Embedding
from rag_system.domain.port.outbound.embedder_port import EmbedderPort


class OpenRouterEmbedder(EmbedderPort):
    def __init__(
        self, api_key: str, model: str, base_url: str = "https://openrouter.ai/api/v1"
    ) -> None:
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/rag-hex",
            },
        )

    async def embed(self, text: str) -> Embedding:
        response = await self._client.post(
            "/embeddings",
            json={
                "model": self._model,
                "input": text,
            },
        )
        response.raise_for_status()
        data = response.json()
        vector = data["data"][0]["embedding"]
        return Embedding(vector=vector, model=self._model, dimensions=len(vector))

    async def embed_batch(self, texts: list[str]) -> list[Embedding]:
        response = await self._client.post(
            "/embeddings",
            json={
                "model": self._model,
                "input": texts,
            },
        )
        response.raise_for_status()
        data = response.json()
        return [
            Embedding(
                vector=item["embedding"],
                model=self._model,
                dimensions=len(item["embedding"]),
            )
            for item in data["data"]
        ]

    async def close(self) -> None:
        await self._client.aclose()
