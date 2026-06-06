# domain/port

Interfaces (ABCs) qui définissent les frontières de l'architecture hexagonale.

- `inbound/` — use cases : query, ingestion
- `outbound/` — services externes : embedder, retriever, LLM, document store, reranker
