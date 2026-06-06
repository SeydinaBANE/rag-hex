import json
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

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
    SearchResultItem,
)
from rag_system.config.container import Container
from rag_system.config.settings import Settings
from rag_system.domain.model.document import Document
from rag_system.domain.model.query import Query

settings = Settings()
container = Container(settings)

app = FastAPI(title="RAG Hex", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest) -> QueryResponse:
    try:
        result = await container.query_service.query(
            Query(text=request.text, top_k=request.top_k, filters=request.filters)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return QueryResponse(
        query=result.query,
        answer=result.answer,
        results=[
            SearchResultItem(chunk_id=r.chunk_id, content=r.content, score=r.score)
            for r in result.results
        ],
    )


@app.post("/query/stream")
async def query_stream_endpoint(request: QueryRequest) -> StreamingResponse:
    query_obj = Query(text=request.text, top_k=request.top_k, filters=request.filters)

    async def event_stream() -> AsyncGenerator[str, None]:
        async for token in container.query_service.query_stream(query_obj):
            yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(request: IngestRequest) -> IngestResponse:
    try:
        doc = Document(
            id=request.document_id,
            content=request.content,
            metadata=dict(request.metadata),
        )
        await container.ingestion_service.ingest(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return IngestResponse(status="ok", document_id=request.document_id)


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    docs = await container.document_store.list()
    summaries = [
        DocumentSummary(
            id=doc.id,
            metadata={k: v for k, v in doc.metadata.items() if k != "_chunk_count"},
            chunk_count=doc.metadata.get("_chunk_count", 0),
        )
        for doc in docs
    ]
    return DocumentListResponse(documents=summaries)


@app.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document(document_id: str) -> DocumentDetail:
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
async def delete_document(document_id: str) -> DeleteResponse:
    doc = await container.document_store.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await container.document_store.delete(document_id)
    return DeleteResponse(status="deleted", document_id=document_id)
