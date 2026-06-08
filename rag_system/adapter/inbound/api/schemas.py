from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: dict[str, str] | None = None


class SearchResultItem(BaseModel):
    chunk_id: str
    content: str
    score: float


class QueryResponse(BaseModel):
    query: str
    answer: str | None = None
    results: list[SearchResultItem] = []


class IngestRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=255, pattern=r"^[\w\-\.]+$")
    content: str = Field(min_length=1, max_length=10_000_000)
    metadata: dict[str, str] = {}


class IngestResponse(BaseModel):
    status: str
    document_id: str


class HealthResponse(BaseModel):
    status: str = "ok"


class ReadinessResponse(BaseModel):
    status: str
    postgres: bool
    qdrant: bool


class DocumentSummary(BaseModel):
    id: str
    metadata: dict[str, Any]
    chunk_count: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentSummary]
    limit: int
    offset: int


class ChunkDetail(BaseModel):
    chunk_id: str
    content: str
    position: int
    page: int | None = None


class DocumentDetail(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any]
    chunks: list[ChunkDetail]


class DeleteResponse(BaseModel):
    status: str
    document_id: str
