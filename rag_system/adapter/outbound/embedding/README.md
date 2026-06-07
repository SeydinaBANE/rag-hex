# adapter/outbound/embedding

Implémente `EmbedderPort` via OpenRouter.

## OpenRouterEmbedder

```python
class OpenRouterEmbedder(EmbedderPort):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1",
    )
```

**Méthodes** :
- `embed(text: str) → Embedding` — embedding d'un texte unique
- `embed_batch(texts: list[str]) → list[Embedding]` — embedding batch

**Détails** :
- Appelle `POST /embeddings` sur OpenRouter
- En-tête `HTTP-Referer: https://github.com/rag-hex` pour le suivi OpenRouter
- Le modèle est configurable via `OPENROUTER_EMBEDDING_MODEL` dans `.env`
- Utilise `httpx.AsyncClient` — le client est créé dans `__init__` et réutilisé

```python
# Exemple de réponse OpenRouter
{
  "data": [{"embedding": [0.123, -0.456, ...], "index": 0}],
  "model": "openai/text-embedding-3-small"
}
```
