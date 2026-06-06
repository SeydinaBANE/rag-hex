export interface QueryRequest {
  text: string;
  top_k?: number;
  filters?: Record<string, string> | null;
}

export interface SearchResultItem {
  chunk_id: string;
  content: string;
  score: number;
}

export interface QueryResponse {
  query: string;
  answer: string | null;
  results: SearchResultItem[];
}

export interface IngestRequest {
  document_id: string;
  content: string;
  metadata?: Record<string, string>;
}

export interface IngestResponse {
  status: string;
  document_id: string;
}

export interface HealthResponse {
  status: string;
}

export interface DocumentSummary {
  id: string;
  metadata: Record<string, string>;
  chunk_count: number;
}

export interface DocumentListResponse {
  documents: DocumentSummary[];
}

export interface ChunkDetail {
  chunk_id: string;
  content: string;
  position: number;
  page: number | null;
}

export interface DocumentDetail {
  id: string;
  content: string;
  metadata: Record<string, string>;
  chunks: ChunkDetail[];
}

export interface DeleteResponse {
  status: string;
  document_id: string;
}
