from rag_system.domain.model.document import ChunkMetadata
from rag_system.domain.model.query import Query, QueryResult, SearchResult


class TestQuery:
    def test_create_query_with_defaults(self) -> None:
        q = Query(text="hello")
        assert q.text == "hello"
        assert q.top_k == 5
        assert q.filters is None

    def test_create_query_with_filters(self) -> None:
        q = Query(text="hello", top_k=10, filters={"source": "pdf"})
        assert q.top_k == 10
        assert q.filters == {"source": "pdf"}

    def test_query_immutable(self) -> None:
        q = Query(text="hello")
        assert q.text == "hello"


class TestSearchResult:
    def test_create_search_result(self) -> None:
        meta = ChunkMetadata(source_document_id="doc-1", position=0)
        sr = SearchResult(chunk_id="chunk-1", content="test", score=0.95, metadata=meta)
        assert sr.score == 0.95


class TestQueryResult:
    def test_empty_query_result(self) -> None:
        qr = QueryResult(query="hello")
        assert qr.results == []
        assert qr.answer is None

    def test_query_result_with_answer(self) -> None:
        qr = QueryResult(query="hello", answer="world")
        assert qr.answer == "world"
