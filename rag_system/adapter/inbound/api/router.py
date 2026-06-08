import json
import logging
import secrets
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from rag_system.adapter.inbound.api.schemas import (
    ChunkDetail,
    DeleteResponse,
    DocumentDetail,
    DocumentListResponse,
    DocumentSummary,
    HealthResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    ReadinessResponse,
    SearchResultItem,
)
from rag_system.config.container import Container
from rag_system.config.settings import Settings
from rag_system.domain.exceptions import EmbeddingError, LLMError, RagError, RetrievalError
from rag_system.domain.model.document import Document
from rag_system.domain.model.query import Query

logger = logging.getLogger(__name__)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)


def _setup_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)


settings = Settings()
container = Container(settings)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _setup_logging()
    if settings.environment == "production" and not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required in production")
    logger.info("RAG Hex starting up (env=%s)", settings.environment)
    yield
    await container.shutdown()
    logger.info("RAG Hex shut down")


app = FastAPI(title="RAG Hex", version="0.1.0", lifespan=lifespan)

security_scheme = HTTPBearer(auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(EmbeddingError)
async def embedding_error_handler(_request: Request, exc: EmbeddingError) -> JSONResponse:
    logger.error("Embedding error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": str(exc)}
    )


@app.exception_handler(LLMError)
async def llm_error_handler(_request: Request, exc: LLMError) -> JSONResponse:
    logger.error("LLM error: %s", exc)
    return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content={"detail": str(exc)})


@app.exception_handler(RetrievalError)
async def retrieval_error_handler(_request: Request, exc: RetrievalError) -> JSONResponse:
    logger.error("Retrieval error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": str(exc)}
    )


@app.exception_handler(RagError)
async def rag_error_handler(_request: Request, exc: RagError) -> JSONResponse:
    logger.error("RAG error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)}
    )


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),  # noqa: B008
) -> None:
    if not settings.api_key:
        return
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )
    if not secrets.compare_digest(credentials.credentials, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.get("/readiness", response_model=ReadinessResponse)
async def readiness() -> JSONResponse:
    postgres_ok = await container.document_store.ping()
    qdrant_ok = await container.retriever.ping()
    all_ok = postgres_ok and qdrant_ok
    payload = ReadinessResponse(
        status="ok" if all_ok else "degraded",
        postgres=postgres_ok,
        qdrant=qdrant_ok,
    ).model_dump()
    return JSONResponse(content=payload, status_code=200 if all_ok else 503)


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequest,
    _: None = Depends(verify_api_key),
) -> QueryResponse:
    result = await container.query_service.query(
        Query(text=request.text, top_k=request.top_k, filters=request.filters)
    )
    return QueryResponse(
        query=result.query,
        answer=result.answer,
        results=[
            SearchResultItem(chunk_id=r.chunk_id, content=r.content, score=r.score)
            for r in result.results
        ],
    )


@app.post("/query/stream")
async def query_stream_endpoint(
    request: QueryRequest,
    _: None = Depends(verify_api_key),
) -> StreamingResponse:
    query_obj = Query(text=request.text, top_k=request.top_k, filters=request.filters)

    async def event_stream() -> AsyncGenerator[str, None]:
        async for token in container.query_service.query_stream(query_obj):
            yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(
    request: IngestRequest,
    _: None = Depends(verify_api_key),
) -> IngestResponse:
    doc = Document(
        id=request.document_id,
        content=request.content,
        metadata=dict(request.metadata),
    )
    await container.ingestion_service.ingest(doc)
    return IngestResponse(status="ok", document_id=request.document_id)


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    limit: int = 50,
    offset: int = 0,
    _: None = Depends(verify_api_key),
) -> DocumentListResponse:
    docs = await container.document_store.list(limit=limit, offset=offset)
    summaries = [
        DocumentSummary(
            id=doc.id,
            metadata={k: v for k, v in doc.metadata.items() if k != "_chunk_count"},
            chunk_count=doc.metadata.get("_chunk_count", 0),
        )
        for doc in docs
    ]
    return DocumentListResponse(documents=summaries, limit=limit, offset=offset)


@app.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    _: None = Depends(verify_api_key),
) -> DocumentDetail:
    doc = await container.document_store.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetail(
        id=doc.id,
        content=doc.content,
        metadata=doc.metadata,
        chunks=[
            ChunkDetail(
                chunk_id=c.id,
                content=c.content,
                position=c.metadata.position,
                page=c.metadata.page,
            )
            for c in (doc.chunks or [])
        ],
    )


@app.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(
    document_id: str,
    _: None = Depends(verify_api_key),
) -> DeleteResponse:
    doc = await container.document_store.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await container.document_store.delete(document_id)
    await container.retriever.delete_chunks(document_id)
    return DeleteResponse(status="deleted", document_id=document_id)
