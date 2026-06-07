# adapter/outbound/storage

Implémente `DocumentStorePort` via PostgreSQL.

## PostgresDocumentStore

```python
class PostgresDocumentStore(DocumentStorePort):
    def __init__(self, database_url: str)
```

**Méthodes** :

| Méthode | Description |
|---|---|
| `store(document)` | Upsert document + ses chunks |
| `get(document_id)` | Document avec chunks, ou `None` |
| `delete(document_id)` | Cascade delete (chunks → document) |
| `list()` | Tous les documents (sans contenu, avec chunk_count) |

**Auto-migration** : les tables sont créées automatiquement au premier appel :

```sql
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    position INTEGER NOT NULL,
    page INTEGER
);
```

**Connexion** : lazy — créée au premier appel, réutilisée ensuite. La connection string est construite par `Settings.database_url` :

```python
postgresql://{user}:{password}@{host}:{port}/{db}
```

**Détails** :
- `list()` ajoute `_chunk_count` aux métadonnées (comptage SQL)
- Les documents sont upsertés (`ON CONFLICT DO UPDATE`)
- Les chunks sont upsertés avec leur position
- `delete()` supprime d'abord les chunks, puis le document
- La connexion est maintenue entre les appels jusqu'à `close()`

**Note** : `storage/` n'a pas de `__init__.py` (contrairement aux autres modules `outbound/`).
