from pydantic import BaseModel


class QueryRequest(BaseModel):
    text: str
    top_k: int = 5
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
    document_id: str
    content: str
    metadata: dict[str, str] = {}


class IngestResponse(BaseModel):
    status: str
    document_id: str


class HealthResponse(BaseModel):
    status: str = "ok"
