import json
from collections.abc import AsyncIterator
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

    def _build_messages(self, prompt: str, context: list[str]) -> list[dict[str, str]]:
        context_block = "\n\n".join(context)
        return [
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
        ]

    async def generate(self, prompt: str, context: list[str]) -> str:
        response = await self._client.post(
            "/chat/completions",
            json={
                "model": self._model,
                "messages": self._build_messages(prompt, context),
            },
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return str(data["choices"][0]["message"]["content"])

    async def generate_stream(self, prompt: str, context: list[str]) -> AsyncIterator[str]:
        async with self._client.stream(
            "POST",
            "/chat/completions",
            json={
                "model": self._model,
                "messages": self._build_messages(prompt, context),
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                chunk: dict[str, Any] = json.loads(payload)
                delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if delta:
                    yield delta

    async def close(self) -> None:
        await self._client.aclose()
