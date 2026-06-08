import json
import logging
from typing import Any

from psycopg_pool import AsyncConnectionPool

from rag_system.domain.model.document import Chunk, ChunkMetadata, Document
from rag_system.domain.port.outbound.document_store_port import DocumentStorePort

logger = logging.getLogger(__name__)


class PostgresDocumentStore(DocumentStorePort):
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._pool: AsyncConnectionPool | None = None

    async def _get_pool(self) -> AsyncConnectionPool:
        if self._pool is None:
            self._pool = AsyncConnectionPool(
                self._database_url,
                min_size=2,
                max_size=10,
                open=False,
            )
            await self._pool.open()
            await self._migrate()
        return self._pool

    async def _migrate(self) -> None:
        if self._pool is None:
            return
        async with self._pool.connection() as conn, conn.cursor() as cur:
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

    async def ping(self) -> bool:
        try:
            pool = await self._get_pool()
            async with pool.connection() as conn, conn.cursor() as cur:
                await cur.execute("SELECT 1")
            return True
        except Exception:
            logger.warning("Postgres ping failed")
            return False

    async def store(self, document: Document) -> None:
        logger.info("Storing document %s", document.id)
        pool = await self._get_pool()
        async with pool.connection() as conn, conn.cursor() as cur:
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
        pool = await self._get_pool()
        async with pool.connection() as conn, conn.cursor() as cur:
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
        logger.info("Deleting document %s", document_id)
        pool = await self._get_pool()
        async with pool.connection() as conn, conn.cursor() as cur:
            await cur.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
            await cur.execute("DELETE FROM documents WHERE id = %s", (document_id,))
            await conn.commit()

    async def list(self, limit: int = 50, offset: int = 0) -> list[Document]:
        pool = await self._get_pool()
        async with pool.connection() as conn, conn.cursor() as cur:
            await cur.execute(
                """
                SELECT d.id, d.metadata,
                       (SELECT COUNT(*) FROM chunks WHERE document_id = d.id) as chunk_count
                FROM documents d
                ORDER BY d.id
                LIMIT %s OFFSET %s
            """,
                (limit, offset),
            )
            rows = await cur.fetchall()
            result: list[Document] = []
            for row in rows:
                doc_id, metadata_raw, chunk_count = row
                metadata = (
                    json.loads(metadata_raw) if isinstance(metadata_raw, str) else metadata_raw
                )
                metadata["_chunk_count"] = chunk_count
                result.append(Document(id=doc_id, content="", metadata=metadata, chunks=None))
            return result

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            logger.info("Postgres connection pool closed")
