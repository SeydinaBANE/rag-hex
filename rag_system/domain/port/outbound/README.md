# domain/port/outbound

Ports de sortie — les services externes dont le domaine a besoin.

Chaque port est une ABC avec des méthodes `@abstractmethod`. Les signatures utilisent uniquement des types du domaine (`Document`, `Embedding`, `Query`, `SearchResult`).

## Ports

| Port | Méthodes | Rôle |
|---|---|---|
| `EmbedderPort` | `embed(text)`, `embed_batch(texts)` | Calcul d'embedding vectoriel |
| `RetrieverPort` | `search(query)` | Recherche vectorielle |
| `LLMPort` | `generate(prompt, context)`, `generate_stream(prompt, context)` | Génération LLM |
| `DocumentStorePort` | `store(doc)`, `get(id)`, `delete(id)`, `list()` | Persistance documents |
| `RerankerPort` | `rerank(query, results)` | Re-ranking des résultats |

## Implémentations disponibles

| Port | Adaptateur | Provider |
|---|---|---|
| `EmbedderPort` | `OpenRouterEmbedder` | OpenRouter `/embeddings` |
| `RetrieverPort` | `QdrantRetriever` | Qdrant |
| `RetrieverPort` | `InMemoryRetriever` | In-memory (tests) |
| `LLMPort` | `OpenRouterLLM` | OpenRouter `/chat/completions` |
| `DocumentStorePort` | `PostgresDocumentStore` | PostgreSQL |
| `RerankerPort` | `CohereReranker` | Cohere `/rerank` |

## Wiring

Le `Container` dans `config/container.py` câble les adaptateurs aux ports. Changer de provider = changer une ligne dans le container :

```python
# config/container.py
@property
def embedder(self) -> EmbedderPort:
    # Switcher ici : OpenRouterEmbedder → HuggingFaceEmbedder
    return OpenRouterEmbedder(...)
```
