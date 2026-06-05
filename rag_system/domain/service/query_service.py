from rag_system.domain.model.query import Query, QueryResult
from rag_system.domain.port.inbound.query_use_case import QueryUseCase
from rag_system.domain.port.outbound.embedder_port import EmbedderPort
from rag_system.domain.port.outbound.llm_port import LLMPort
from rag_system.domain.port.outbound.reranker_port import RerankerPort
from rag_system.domain.port.outbound.retriever_port import RetrieverPort


class QueryService(QueryUseCase):
    def __init__(
        self,
        embedder: EmbedderPort,
        retriever: RetrieverPort,
        llm: LLMPort,
        reranker: RerankerPort | None = None,
    ) -> None:
        self._embedder = embedder
        self._retriever = retriever
        self._llm = llm
        self._reranker = reranker

    async def query(self, query: Query) -> QueryResult:
        retrieved = await self._retriever.search(query)

        if self._reranker is not None and retrieved:
            retrieved = await self._reranker.rerank(query.text, retrieved)

        if not retrieved:
            return QueryResult(query=query.text, results=[])

        context = [r.content for r in retrieved]

        answer = await self._llm.generate(
            prompt=query.text,
            context=context,
        )

        return QueryResult(query=query.text, results=retrieved, answer=answer)
