# adapter/inbound

Points d'entrée du système. Deux modes d'interaction : API REST et CLI.

| Sous-dossier | Technologie | Exposition |
|---|---|---|
| `api/` | FastAPI + Pydantic | REST : `/query`, `/ingest`, `/health`, `/documents` |
| `cli/` | Typer | Ligne de commande : `rag ingest`, `rag query` |

Les deux utilisent le `Container` (config/container.py) pour accéder aux services :

```python
settings = Settings()
container = Container(settings)
result = await container.query_service.query(Query(text=text))
```
