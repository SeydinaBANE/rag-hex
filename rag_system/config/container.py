from rag_system.adapter.outbound.embedding.openrouter_embedder import OpenRouterEmbedder
from rag_system.adapter.outbound.llm.openrouter_llm import OpenRouterLLM
from rag_system.adapter.outbound.retrieval.qdrant_retriever import QdrantRetriever
from rag_system.adapter.outbound.storage.postgres_document_store import PostgresDocumentStore
from rag_system.config.settings import Settings
from rag_system.domain.port.outbound.document_store_port import DocumentStorePort
from rag_system.domain.port.outbound.embedder_port import EmbedderPort
from rag_system.domain.port.outbound.llm_port import LLMPort
from rag_system.domain.port.outbound.reranker_port import RerankerPort
from rag_system.domain.port.outbound.retriever_port import RetrieverPort
from rag_system.domain.service.ingestion_service import IngestionService
from rag_system.domain.service.query_service import QueryService


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._embedder: EmbedderPort | None = None
        self._retriever: RetrieverPort | None = None
        self._llm: LLMPort | None = None
        self._document_store: DocumentStorePort | None = None
        self._reranker: RerankerPort | None = None
        self._query_service: QueryService | None = None
        self._ingestion_service: IngestionService | None = None

    @property
    def embedder(self) -> EmbedderPort:
        if self._embedder is None:
            self._embedder = OpenRouterEmbedder(
                api_key=self.settings.openrouter_api_key,
                model=self.settings.openrouter_embedding_model,
                base_url=self.settings.openrouter_base_url,
            )
        return self._embedder

    @property
    def retriever(self) -> RetrieverPort:
        if self._retriever is None:
            self._retriever = QdrantRetriever(
                url=self.settings.qdrant_url,
                collection_name=self.settings.qdrant_collection,
            )
        return self._retriever

    @property
    def llm(self) -> LLMPort:
        if self._llm is None:
            self._llm = OpenRouterLLM(
                api_key=self.settings.openrouter_api_key,
                model=self.settings.openrouter_llm_model,
                base_url=self.settings.openrouter_base_url,
            )
        return self._llm

    @property
    def document_store(self) -> DocumentStorePort:
        if self._document_store is None:
            self._document_store = PostgresDocumentStore(
                database_url=self.settings.database_url,
            )
        return self._document_store

    @property
    def reranker(self) -> RerankerPort | None:
        return self._reranker

    @property
    def query_service(self) -> QueryService:
        if self._query_service is None:
            self._query_service = QueryService(
                embedder=self.embedder,
                retriever=self.retriever,
                llm=self.llm,
                reranker=self.reranker,
            )
        return self._query_service

    @property
    def ingestion_service(self) -> IngestionService:
        if self._ingestion_service is None:
            self._ingestion_service = IngestionService(
                embedder=self.embedder,
                document_store=self.document_store,
                retriever=self.retriever,
                chunk_size=self.settings.chunk_size,
                chunk_overlap=self.settings.chunk_overlap,
            )
        return self._ingestion_service

    async def shutdown(self) -> None:
        if self._embedder is not None:
            await self._embedder.close()
        if self._llm is not None:
            await self._llm.close()
        if self._retriever is not None:
            await self._retriever.close()
        if self._document_store is not None:
            await self._document_store.close()
