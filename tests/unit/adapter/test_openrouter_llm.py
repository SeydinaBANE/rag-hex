import json

import httpx
import pytest
import respx

from rag_system.adapter.outbound.llm.openrouter_llm import OpenRouterLLM
from rag_system.domain.exceptions import LLMError


@pytest.fixture
def llm() -> OpenRouterLLM:
    return OpenRouterLLM(
        api_key="sk-or-v1-test",
        model="anthropic/claude-sonnet-20241022",
        base_url="https://openrouter.ai/api/v1",
    )


class TestOpenRouterLLM:
    @respx.mock
    async def test_generate_returns_content(self, llm: OpenRouterLLM) -> None:
        route = respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                json={"choices": [{"message": {"content": "Voici la réponse."}}]},
            )
        )

        answer = await llm.generate(prompt="Quel temps fait-il ?", context=["Il fait beau."])

        assert answer == "Voici la réponse."
        assert route.called

    @respx.mock
    async def test_generate_raises_on_http_error(self, llm: OpenRouterLLM) -> None:
        respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=httpx.Response(401, json={"error": "unauthorized"})
        )

        with pytest.raises(LLMError):
            await llm.generate(prompt="test", context=[])

    @respx.mock
    async def test_generate_sends_expected_payload(self, llm: OpenRouterLLM) -> None:
        route = respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})
        )

        await llm.generate(prompt="Question ?", context=["ctx1", "ctx2"])

        assert route.called
        sent = json.loads(route.calls.last.request.content)
        assert sent["model"] == "anthropic/claude-sonnet-20241022"
        assert "ctx1" in sent["messages"][1]["content"]
        assert "Question ?" in sent["messages"][1]["content"]

    @respx.mock
    async def test_generate_stream_yields_tokens(self, llm: OpenRouterLLM) -> None:
        def sse_chunk(content: str) -> str:
            return f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"

        chunks = [sse_chunk("Hello"), sse_chunk(" world"), "data: [DONE]\n\n"]
        route = respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=httpx.Response(200, text="".join(chunks))
        )

        tokens = [t async for t in llm.generate_stream(prompt="hi", context=["ctx"])]

        assert tokens == ["Hello", " world"]
        assert route.called

    @respx.mock
    async def test_generate_stream_empty_delta(self, llm: OpenRouterLLM) -> None:
        route = respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                text="data: [DONE]\n\n",
            )
        )

        tokens = [t async for t in llm.generate_stream(prompt="hi", context=["ctx"])]
        assert tokens == []
        assert route.called
