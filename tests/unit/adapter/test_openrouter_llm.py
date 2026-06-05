import json

import httpx
import pytest
import respx

from rag_system.adapter.outbound.llm.openrouter_llm import OpenRouterLLM


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
                json={
                    "choices": [
                        {"message": {"content": "Voici la réponse."}}
                    ]
                },
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

        with pytest.raises(httpx.HTTPStatusError):
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
