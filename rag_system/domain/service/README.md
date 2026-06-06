# domain/service

Orchestration métier pure. Dépend uniquement des ports (ABCs), jamais des adaptateurs.

| Fichier | Use case | Orchestration |
|---|---|---|
| `query_service.py` | QueryUseCase | embed → retrieve → rerank → generate |
| `ingestion_service.py` | IngestionUseCase | chunk → embed_batch → store |
