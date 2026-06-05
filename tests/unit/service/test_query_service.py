from unittest.mock import AsyncMock

import pytest

from rag_system.domain.model.document import ChunkMetadata
from rag_system.domain.model.query import Query, QueryResult, SearchResult
from rag_system.domain.service.query_service import QueryService


class TestQueryService:
    @pytest.fixture
    def mock_ports(self) -> tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock]:
        return AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock()

    @pytest.fixture
    def service(
        self, mock_ports: tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock]
    ) -> QueryService:
        embedder, retriever, llm, reranker = mock_ports
        return QueryService(embedder=embedder, retriever=retriever, llm=llm, reranker=reranker)

    async def test_query_with_results(
        self, service: QueryService, mock_ports: tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock]
    ) -> None:
        _, retriever, llm, reranker = mock_ports
        meta = ChunkMetadata(source_document_id="doc-1", position=0)
        results = [SearchResult(chunk_id="c1", content="hello world", score=0.9, metadata=meta)]
        retriever.search = AsyncMock(return_value=results)
        reranker.rerank = AsyncMock(return_value=results)
        llm.generate = AsyncMock(return_value="some answer")

        result = await service.query(Query(text="hello"))

        assert isinstance(result, QueryResult)
        assert result.query == "hello"
        assert len(result.results) == 1
        assert result.answer == "some answer"
        reranker.rerank.assert_awaited_once()

    async def test_query_no_results(
        self, service: QueryService, mock_ports: tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock]
    ) -> None:
        _, retriever, llm, _ = mock_ports
        retriever.search = AsyncMock(return_value=[])

        result = await service.query(Query(text="hello"))

        assert result.results == []
        assert result.answer is None
        llm.generate.assert_not_called()

    async def test_query_skips_reranker_when_none(self) -> None:
        embedder = AsyncMock()
        retriever = AsyncMock()
        llm = AsyncMock()
        service = QueryService(embedder=embedder, retriever=retriever, llm=llm, reranker=None)

        meta = ChunkMetadata(source_document_id="doc-1", position=0)
        results = [SearchResult(chunk_id="c1", content="test", score=0.9, metadata=meta)]
        retriever.search = AsyncMock(return_value=results)
        llm.generate = AsyncMock(return_value="answer")

        result = await service.query(Query(text="test"))

        assert result.answer == "answer"
        assert len(result.results) == 1
