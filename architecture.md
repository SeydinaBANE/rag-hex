rag_system/
│
├── domain/                          ← cœur pur, zéro dépendance externe
│   ├── model/
│   │   ├── document.py              # Document, Chunk, ChunkMetadata
│   │   ├── query.py                 # Query, QueryResult, SearchResult
│   │   └── embedding.py             # Embedding (value object)
│   │
│   ├── port/
│   │   ├── inbound/
│   │   │   ├── query_use_case.py    # QueryUseCase (ABC)
│   │   │   └── ingestion_use_case.py# IngestionUseCase (ABC)
│   │   │
│   │   └── outbound/
│   │       ├── embedder_port.py     # EmbedderPort (ABC)
│   │       ├── retriever_port.py    # RetrieverPort (ABC)
│   │       ├── llm_port.py          # LLMPort (ABC)
│   │       ├── document_store_port.py# DocumentStorePort (ABC)
│   │       └── reranker_port.py     # RerankerPort (ABC)
│   │
│   └── service/
│       ├── query_service.py         # orchestration retrieval → generation
│       └── ingestion_service.py     # orchestration parse → chunk → embed → index
│
├── adapter/
│   ├── inbound/
│   │   ├── api/
│   │   │   ├── router.py            # FastAPI routes
│   │   │   └── schemas.py           # Pydantic request/response
│   │   └── cli/
│   │       └── ingest_cli.py        # typer CLI pour l'ingestion batch
│   │
│   └── outbound/
│       ├── embedding/
│       │   ├── openai_embedder.py   # OpenAIEmbedder(EmbedderPort)
│       │   └── local_embedder.py    # HuggingFaceEmbedder(EmbedderPort)
│       ├── retrieval/
│       │   ├── qdrant_retriever.py  # QdrantRetriever(RetrieverPort)
│       │   └── in_memory_retriever.py# pour les tests
│       ├── llm/
│       │   ├── anthropic_llm.py     # AnthropicLLM(LLMPort)
│       │   └── openai_llm.py        # OpenAILLM(LLMPort)
│       ├── reranker/
│       │   ├── cohere_reranker.py   # CohereReranker(RerankerPort)
│       │   └── cross_encoder_reranker.py
│       └── storage/
│           ├── s3_document_store.py
│           └── postgres_document_store.py
│
├── config/
│   └── container.py                 # Composition Root (DI)
│
├── tests/
│   ├── unit/                        # testent le domaine seul
│   │   ├── test_query_service.py
│   │   └── test_ingestion_service.py
│   └── integration/                 # testent les adaptateurs réels
│       ├── test_qdrant_retriever.py
│       └── test_openai_embedder.py