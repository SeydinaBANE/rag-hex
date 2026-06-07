# adapter

Implémentations concrètes des ports. Toute l'infrastructure (HTTP, DB, CLI, API) vit ici.

Contrairement au `domain/`, les adaptateurs peuvent importer `httpx`, `fastapi`, `qdrant-client`, `psycopg`, etc. Ils ne doivent jamais contenir de logique métier — uniquement du câblage et de l'IO.

## Structure

```
adapter/
├── inbound/           ← Points d'entrée du système
│   ├── api/           ← FastAPI REST
│   └── cli/           ← Typer CLI
└── outbound/          ← Connecteurs vers services externes
    ├── embedding/     ← OpenRouterEmbedder (EmbedderPort)
    ├── llm/           ← OpenRouterLLM (LLMPort)
    ├── retrieval/     ← QdrantRetriever, InMemoryRetriever (RetrieverPort)
    ├── reranker/      ← CohereReranker (RerankerPort)
    └── storage/       ← PostgresDocumentStore (DocumentStorePort)
```

## Contrat

- Chaque adaptateur implémente exactement un port du domaine
- Tous les adaptateurs exposent une méthode `close()` pour le cleanup
- Les clients HTTP sont créés dans `__init__` et réutilisés
- Les connexions DB sont lazy (créées au premier appel)
