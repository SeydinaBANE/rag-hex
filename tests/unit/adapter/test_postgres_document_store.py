from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rag_system.adapter.outbound.storage.postgres_document_store import PostgresDocumentStore
from rag_system.domain.model.document import Chunk, ChunkMetadata, Document


def _make_pool_mock() -> tuple[MagicMock, MagicMock, AsyncMock]:
    mock_cur = AsyncMock()

    mock_conn = MagicMock()
    mock_conn.commit = AsyncMock()
    mock_conn.cursor.return_value.__aenter__ = AsyncMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__aexit__ = AsyncMock(return_value=False)

    mock_pool = MagicMock()
    mock_pool.connection.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)

    return mock_pool, mock_conn, mock_cur


@pytest.fixture
def store() -> PostgresDocumentStore:
    return PostgresDocumentStore(database_url="postgresql://test:test@localhost/test")


class TestPostgresDocumentStore:
    async def test_ping_returns_true_on_success(self, store: PostgresDocumentStore) -> None:
        mock_pool, _, mock_cur = _make_pool_mock()
        with patch.object(store, "_get_pool", AsyncMock(return_value=mock_pool)):
            result = await store.ping()

        assert result is True
        mock_cur.execute.assert_awaited_once_with("SELECT 1")

    async def test_ping_returns_false_on_failure(self, store: PostgresDocumentStore) -> None:
        with patch.object(store, "_get_pool", AsyncMock(side_effect=Exception("refused"))):
            result = await store.ping()

        assert result is False

    async def test_store_document(self, store: PostgresDocumentStore) -> None:
        mock_pool, mock_conn, mock_cur = _make_pool_mock()
        doc = Document(id="doc-1", content="hello world", metadata={"source": "test"})

        with patch.object(store, "_get_pool", AsyncMock(return_value=mock_pool)):
            await store.store(doc)

        assert mock_cur.execute.await_count == 1
        mock_conn.commit.assert_awaited_once()

    async def test_store_document_with_chunks(self, store: PostgresDocumentStore) -> None:
        mock_pool, mock_conn, mock_cur = _make_pool_mock()
        doc = Document(
            id="doc-1",
            content="hello world",
            metadata={},
            chunks=[
                Chunk(
                    id="doc-1__chunk_0",
                    content="hello",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=0),
                ),
                Chunk(
                    id="doc-1__chunk_1",
                    content="world",
                    metadata=ChunkMetadata(source_document_id="doc-1", position=1),
                ),
            ],
        )

        with patch.object(store, "_get_pool", AsyncMock(return_value=mock_pool)):
            await store.store(doc)

        assert mock_cur.execute.await_count == 3

    async def test_get_returns_none_when_not_found(self, store: PostgresDocumentStore) -> None:
        mock_pool, _, mock_cur = _make_pool_mock()
        mock_cur.fetchone = AsyncMock(return_value=None)

        with patch.object(store, "_get_pool", AsyncMock(return_value=mock_pool)):
            result = await store.get("nonexistent")

        assert result is None

    async def test_list_applies_limit_and_offset(self, store: PostgresDocumentStore) -> None:
        mock_pool, _, mock_cur = _make_pool_mock()
        mock_cur.fetchall = AsyncMock(return_value=[])

        with patch.object(store, "_get_pool", AsyncMock(return_value=mock_pool)):
            result = await store.list(limit=10, offset=20)

        assert result == []
        call_args = mock_cur.execute.call_args
        assert call_args[0][1] == (10, 20)

    async def test_close_drains_pool(self, store: PostgresDocumentStore) -> None:
        mock_pool = AsyncMock()
        store._pool = mock_pool

        await store.close()

        mock_pool.close.assert_awaited_once()

    async def test_close_is_noop_when_pool_not_opened(self, store: PostgresDocumentStore) -> None:
        await store.close()
