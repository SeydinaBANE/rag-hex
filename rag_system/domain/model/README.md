# domain/model

Value objects et entités du domaine RAG. Toutes sont des `@dataclass` pures — pas de logique métier, pas de dépendances externes.

## Classes

| Fichier | Classe | Type | Description |
|---|---|---|---|
| `document.py` | `Document` | `@dataclass` | Document source (id, content, metadata, chunks) |
| `document.py` | `Chunk` | `@dataclass` | Découpe de document (id, content, metadata, embedding) |
| `document.py` | `ChunkMetadata` | `@dataclass` | Métadonnées de chunk (source_document_id, page, position) |
| `embedding.py` | `Embedding` | `@dataclass(frozen)` | Vecteur d'embedding (vector, model, dimensions) |
| `query.py` | `Query` | `@dataclass(frozen)` | Requête utilisateur (text, top_k, filters) |
| `query.py` | `SearchResult` | `@dataclass(frozen)` | Résultat de recherche (chunk_id, content, score, metadata) |
| `query.py` | `QueryResult` | `@dataclass` | Réponse complète (query, results, answer) |

## Validation

`Embedding` valide ses dimensions en `__post_init__` :

```python
@dataclass(frozen=True)
class Embedding:
    vector: list[float]
    model: str
    dimensions: int

    def __post_init__(self) -> None:
        if self.dimensions <= 0:
            raise ValueError("dimensions must be positive")
        if len(self.vector) != self.dimensions:
            raise ValueError("vector length does not match dimensions")
```

## Contrat

- Toutes les classes sont des dataclasses pures (pas de BaseModel, pas d'ORM)
- `Embedding`, `Query` et `SearchResult` sont frozen (immuables)
- `Document.chunks` peut être `None` ou une liste de `Chunk`
- `Chunk.embedding` peut être `None` (avant embedding)
