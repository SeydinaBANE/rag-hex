# domain/service

Orchestration métier pure. Les services dépendent uniquement des ports (ABCs), jamais des adaptateurs concrets.

## QueryService

```python
class QueryService(QueryUseCase):
    def __init__(
        self,
        embedder: EmbedderPort,
        retriever: RetrieverPort,
        llm: LLMPort,
        reranker: RerankerPort | None = None,
    )
```

**Orchestration `query()`** :
1. `embedder.embed(query.text)` → vecteur
2. `retriever.search(query)` → `SearchResult[]`
3. `reranker.rerank(query.text, results)` si reranker présent
4. `llm.generate(context, prompt)` → réponse texte
5. retourne `QueryResult(answer, results)`

**Orchestration `query_stream()`** :
1-3 identique
4. `llm.generate_stream(context, prompt)` → AsyncIterator[str] (SSE)

## IngestionService

```python
class IngestionService(IngestionUseCase):
    def __init__(
        self,
        embedder: EmbedderPort,
        document_store: DocumentStorePort,
        retriever: RetrieverPort,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    )
```

**Orchestration `ingest()`** :
1. `_chunk_document(document)` → découpage en chunks (taille 512, overlap 64)
2. `embedder.embed_batch(chunks_texts)` → vecteurs
3. Associe chaque embedding à son chunk
4. `document_store.store(document)` → persist en base

**Chunking** : découpage simple par position avec chevauchement. IDs des chunks : `{document_id}__chunk_{position}`.

## Test

```python
# Les services se testent en mockant les ports
mock_retriever = AsyncMock(spec=RetrieverPort)
mock_retriever.search = AsyncMock(return_value=[...])

service = QueryService(embedder=mock_embedder, retriever=mock_retriever, llm=mock_llm)
result = await service.query(Query(text="hello"))
```
