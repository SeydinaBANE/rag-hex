import httpx
import pytest
import respx

from rag_system.adapter.outbound.embedding.openrouter_embedder import OpenRouterEmbedder
from rag_system.domain.exceptions import EmbeddingError


@pytest.fixture
def embedder() -> OpenRouterEmbedder:
    return OpenRouterEmbedder(
        api_key="sk-or-v1-test",
        model="openai/text-embedding-3-small",
        base_url="https://openrouter.ai/api/v1",
    )


class TestOpenRouterEmbedder:
    @respx.mock
    async def test_embed_single_text(self, embedder: OpenRouterEmbedder) -> None:
        route = respx.post("https://openrouter.ai/api/v1/embeddings").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [{"embedding": [0.1, 0.2, 0.3]}],
                    "model": "openai/text-embedding-3-small",
                },
            )
        )

        emb = await embedder.embed("hello")

        assert emb.vector == [0.1, 0.2, 0.3]
        assert emb.dimensions == 3
        assert route.called

    @respx.mock
    async def test_embed_batch(self, embedder: OpenRouterEmbedder) -> None:
        route = respx.post("https://openrouter.ai/api/v1/embeddings").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {"embedding": [0.1, 0.2]},
                        {"embedding": [0.3, 0.4]},
                    ],
                    "model": "openai/text-embedding-3-small",
                },
            )
        )

        embeddings = await embedder.embed_batch(["hello", "world"])

        assert len(embeddings) == 2
        assert embeddings[0].dimensions == 2
        assert embeddings[1].vector == [0.3, 0.4]
        assert route.called

    @respx.mock
    async def test_embed_raises_on_http_error(self, embedder: OpenRouterEmbedder) -> None:
        respx.post("https://openrouter.ai/api/v1/embeddings").mock(
            return_value=httpx.Response(429, json={"error": "rate limit"})
        )

        with pytest.raises(EmbeddingError):
            await embedder.embed("test")
