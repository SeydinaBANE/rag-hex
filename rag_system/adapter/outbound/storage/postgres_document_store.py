import json
from typing import Any

import psycopg
from psycopg import AsyncConnection

from rag_system.domain.model.document import Chunk, ChunkMetadata, Document
from rag_system.domain.port.outbound.document_store_port import DocumentStorePort


class PostgresDocumentStore(DocumentStorePort):
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._conn: AsyncConnection | None = None

    async def _ensure_connection(self) -> AsyncConnection:
        if self._conn is None or self._conn.closed:
            self._conn = await psycopg.AsyncConnection.connect(self._database_url)
            await self._migrate()
        return self._conn

    async def _migrate(self) -> None:
        if self._conn is None:
            return
        conn = self._conn
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{}'
                );
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    page INTEGER
                );
            """)
        await conn.commit()

    async def store(self, document: Document) -> None:
        conn = await self._ensure_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO documents (id, content, metadata) VALUES (%s, %s, %s) "
                "ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, "
                "metadata = EXCLUDED.metadata",
                (document.id, document.content, json.dumps(document.metadata)),
            )

            if document.chunks:
                for chunk in document.chunks:
                    await cur.execute(
                        "INSERT INTO chunks (id, document_id, content, position, page) "
                        "VALUES (%s, %s, %s, %s, %s) "
                        "ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, "
                        "position = EXCLUDED.position, page = EXCLUDED.page",
                        (
                            chunk.id,
                            document.id,
                            chunk.content,
                            chunk.metadata.position,
                            chunk.metadata.page,
                        ),
                    )
        await conn.commit()

    async def get(self, document_id: str) -> Document | None:
        conn = await self._ensure_connection()
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, content, metadata FROM documents WHERE id = %s",
                (document_id,),
            )
            row = await cur.fetchone()
            if row is None:
                return None

            doc_id, content, metadata_raw = row
            metadata: dict[str, Any] = (
                json.loads(metadata_raw) if isinstance(metadata_raw, str) else metadata_raw
            )

            await cur.execute(
                "SELECT id, content, position, page FROM chunks "
                "WHERE document_id = %s ORDER BY position",
                (document_id,),
            )
            chunk_rows = await cur.fetchall()
            chunks = [
                Chunk(
                    id=cr[0],
                    content=cr[1],
                    metadata=ChunkMetadata(
                        source_document_id=document_id,
                        position=cr[2],
                        page=cr[3],
                    ),
                )
                for cr in chunk_rows
            ]

            return Document(id=doc_id, content=content, metadata=metadata, chunks=chunks or None)

    async def delete(self, document_id: str) -> None:
        conn = await self._ensure_connection()
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
            await cur.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        await conn.commit()

    async def close(self) -> None:
        if self._conn is not None and not self._conn.closed:
            await self._conn.close()
