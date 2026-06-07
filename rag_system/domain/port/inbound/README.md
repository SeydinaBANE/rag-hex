# domain/port/inbound

Ports d'entrée — les use cases que le système expose au monde extérieur.

## QueryUseCase

```python
class QueryUseCase(ABC):
    @abstractmethod
    async def query(self, query: Query) -> QueryResult: ...

    @abstractmethod
    def query_stream(self, query: Query) -> AsyncIterator[str]: ...
```

Deux modes :
- `query()` — réponse complète (attends tout le résultat)
- `query_stream()` — streaming SSE token par token depuis le LLM

## IngestionUseCase

```python
class IngestionUseCase(ABC):
    @abstractmethod
    async def ingest(self, document: Document) -> None: ...
```

Prend un `Document` brut, le découpe en chunks, calcule les embeddings, et persist dans le document store + vector store.

## Implémentations

Les implémentations concrètes vivent dans `domain/service/` :
- `QueryService(QueryUseCase)`
- `IngestionService(IngestionUseCase)`
