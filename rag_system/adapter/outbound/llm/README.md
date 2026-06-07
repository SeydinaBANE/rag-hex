# adapter/outbound/llm

Implémente `LLMPort` via OpenRouter.

## OpenRouterLLM

```python
class OpenRouterLLM(LLMPort):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1",
    )
```

**Méthodes** :
- `generate(prompt: str, context: list[str]) → str` — réponse complète
- `generate_stream(prompt: str, context: list[str]) → AsyncIterator[str]` — streaming token par token

**Construction du prompt** :

```python
messages = [
    {"role": "system", "content": "Answer based solely on provided context."},
    {"role": "user", "content": "Contexte :\n{context}\n\nQuestion : {prompt}"},
]
```

**Streaming** :
- Utilise `httpx.AsyncClient.stream("POST", ...)` avec `stream=True`
- Parse les lignes `data: {...}` SSE
- S'arrête sur `data: [DONE]`
- Sort chaque token un par un via `yield`

**Détails** :
- Appelle `POST /chat/completions` sur OpenRouter
- En-tête `HTTP-Referer: https://github.com/rag-hex`
- Le modèle est configurable via `OPENROUTER_MODEL` dans `.env`
- Gère le cleanup avec `async close()`
