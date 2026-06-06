import json
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from rag_system.adapter.inbound.api.schemas import (
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
