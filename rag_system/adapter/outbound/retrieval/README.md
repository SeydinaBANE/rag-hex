# adapter/outbound/retrieval

Implémente `RetrieverPort` — recherche vectorielle et textuelle.

## QdrantRetriever

```python
class QdrantRetriever(RetrieverPort):
    def __init__(
        self,
        url: str,
        collection_name: str = "rag_documents",
    )
```

**État actuel** : ⚠️ `search()` est un stub qui retourne `[]`. Les méthodes `ensure_collection()` et `upsert_chunk()` existent mais ne sont pas utilisées par les services.

```
QdrantRetriever.search(query) → []  # stub
```

Pour activer la recherche vectorielle complète :
1. Appeler `ensure_collection(vector_size)` au démarrage
2. Appeler `upsert_chunk(chunk_id, embedding, payload)` pendant l'ingestion
3. Implémenter `search()` avec `client.search()`

La collection utilise `distance: COSINE`. Les points sont indexés par `hash(chunk_id)`.

## InMemoryRetriever

```python
class InMemoryRetriever(RetrieverPort):
    def __init__(self)
```

**Usage** : tests unitaires et développement rapide.

- `add_chunk(chunk_id, content, metadata)` — ajoute un chunk manuellement
- `clear()` — vide tous les chunks
- `search(query)` — scoring textuel simple (ratio de mots communs)
- Utilise `heapq.nlargest()` pour `top_k`
- Pas de persistance, pas de vectorisation

```python
retriever = InMemoryRetriever()
retriever.add_chunk("c1", "Le chat mange une souris", ChunkMetadata(...))
results = await retriever.search(Query(text="chat", top_k=5))
```
