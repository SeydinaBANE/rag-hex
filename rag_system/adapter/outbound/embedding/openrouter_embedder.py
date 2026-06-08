import logging

from httpx import AsyncClient, AsyncHTTPTransport, HTTPStatusError, Timeout

from rag_system.domain.exceptions import EmbeddingError
from rag_system.domain.model.embedding import Embedding
from rag_system.domain.port.outbound.embedder_port import EmbedderPort

logger = logging.getLogger(__name__)


class OpenRouterEmbedder(EmbedderPort):
    def __init__(
        self, api_key: str, model: str, base_url: str = "https://openrouter.ai/api/v1"
    ) -> None:
        self._model = model
        transport = AsyncHTTPTransport(retries=3)
        self._client = AsyncClient(
            base_url=base_url,
            transport=transport,
            timeout=Timeout(60.0, connect=15.0),
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/rag-hex",
            },
        )

    async def embed(self, text: str) -> Embedding:
        logger.debug("Embedding single text via %s", self._model)
        try:
            response = await self._client.post(
                "/embeddings",
                json={"model": self._model, "input": text},
            )
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise EmbeddingError(
                f"OpenRouter embeddings failed: {exc.response.status_code}"
            ) from exc
        data = response.json()
        vector = data["data"][0]["embedding"]
        return Embedding(vector=vector, model=self._model, dimensions=len(vector))

    async def embed_batch(self, texts: list[str]) -> list[Embedding]:
        logger.info("Embedding batch of %d texts via %s", len(texts), self._model)
        try:
            response = await self._client.post(
                "/embeddings",
                json={"model": self._model, "input": texts},
            )
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise EmbeddingError(
                f"OpenRouter embeddings failed: {exc.response.status_code}"
            ) from exc
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
