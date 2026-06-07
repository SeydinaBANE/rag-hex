# domain/port

Interfaces (ABCs) qui définissent les frontières de l'architecture hexagonale.

Les ports sont le contrat entre le cœur métier et le monde extérieur. Le domaine dépend des ports (abstractions) — les adaptateurs implémentent les ports.

## Structure

```
port/
├── inbound/           ← Use cases (entrées du système)
│   ├── query_use_case.py
│   └── ingestion_use_case.py
└── outbound/          ← Services externes (sorties du système)
    ├── embedder_port.py
    ├── retriever_port.py
    ├── llm_port.py
    ├── document_store_port.py
    └── reranker_port.py
```

## Principe

```python
# Le port — domaine pur, pas d'import externe
class RetrieverPort(ABC):
    @abstractmethod
    async def search(self, query: Query) -> list[SearchResult]: ...

# L'implémentation — dans adapter/outbound/, peut importer httpx/qdrant
class QdrantRetriever(RetrieverPort):
    async def search(self, query: Query) -> list[SearchResult]:
        # httpx, qdrant-client autorisés ici
        ...
```
