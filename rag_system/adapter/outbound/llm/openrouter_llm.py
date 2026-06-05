from typing import Any

import httpx

from rag_system.domain.port.outbound.llm_port import LLMPort


class OpenRouterLLM(LLMPort):
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

    async def generate(self, prompt: str, context: list[str]) -> str:
        context_block = "\n\n".join(context)
        response = await self._client.post(
            "/chat/completions",
            json={
                "model": self._model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. Answer the user's question "
                            "based solely on the provided context. If the context does "
                            "not contain the answer, say so."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Contexte :\n{context_block}\n\nQuestion : {prompt}",
                    },
                ],
            },
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return str(data["choices"][0]["message"]["content"])

    async def close(self) -> None:
        await self._client.aclose()
