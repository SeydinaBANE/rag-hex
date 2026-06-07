# adapter/outbound/reranker

Implémente `RerankerPort` via Cohere.

## CohereReranker

```python
class CohereReranker(RerankerPort):
    def __init__(
        self,
        api_key: str,
        model: str = "rerank-multilingual-v3.0",
    )
```

**Méthode** :
- `rerank(query: str, results: list[SearchResult]) → list[SearchResult]` — re-classe les résultats par pertinence

**Détails** :
- Appelle `POST /rerank` sur Cohere
- Envoie `query` + `documents` (contenu textuel de chaque résultat)
- Recoit `results[{index, relevance_score}]`
- Retourne les `SearchResult` réordonnés avec les nouveaux scores
- Utilise `httpx.AsyncClient` avec API key en header

## État actuel

⚠️ **Non câblé** dans le `Container`. La propriété `container.reranker` retourne toujours `None` :

```python
@property
def reranker(self) -> RerankerPort | None:
    return self._reranker  # jamais initialisé
```

Pour activer le reranker, modifier `config/container.py` :

```python
@property
def reranker(self) -> RerankerPort | None:
    if self._reranker is None:
        self._reranker = CohereReranker(api_key=os.environ["COHERE_API_KEY"])
    return self._reranker
```
