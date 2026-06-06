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
