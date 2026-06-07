# adapter/inbound/cli

CLI Typer pour l'ingestion et les requêtes en ligne de commande.

## Utilisation

```bash
# Ingestion d'un fichier texte
uv run python -m rag_system.adapter.inbound.cli.ingest_cli ingest \
    --file document.txt \
    --document-id mon-doc

# Query interactive
uv run python -m rag_system.adapter.inbound.cli.ingest_cli query \
    --text "Quelle est la réponse ?" \
    --top-k 5
```

## Commandes

| Commande | Arguments | Description |
|---|---|---|
| `ingest` | `--file` (obligatoire), `--document-id` (optionnel) | Lit un fichier et l'ingère |
| `query` | `--text` (obligatoire), `--top-k` (défaut=5) | Pose une question au RAG |

## Détails d'implémentation

- Utilise `asyncio.run()` pour les appels asynchrones au container
- Le document_id par défaut est le stem du nom de fichier
- Les métadonnées automatiques : `source` (path), `filename` (nom du fichier)
- Gère les erreurs : fichier introuvable → exit code 1 + message stderr

```python
settings = Settings()
container = Container(settings)
doc = Document(id=doc_id, content=content, metadata={"source": str(path), "filename": path.name})
asyncio.run(container.ingestion_service.ingest(doc))
```
