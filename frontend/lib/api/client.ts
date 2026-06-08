const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function authHeaders(): Record<string, string> {
  return API_KEY ? { Authorization: `Bearer ${API_KEY}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(response.status, body || response.statusText);
  }

  return response.json() as Promise<T>;
}

export const api = {
  query: (body: { text: string; top_k?: number }) =>
    request<import("@/lib/types/api").QueryResponse>("/query", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  ingest: (body: import("@/lib/types/api").IngestRequest) =>
    request<import("@/lib/types/api").IngestResponse>("/ingest", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  health: () => request<import("@/lib/types/api").HealthResponse>("/health"),

  queryStream: (body: {
    text: string;
    top_k?: number;
  }): Promise<ReadableStream<Uint8Array> | null> => {
    const url = `${BASE_URL}/query/stream`;
    return fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(body),
    }).then((res) => res.body);
  },

  listDocuments: () =>
    request<import("@/lib/types/api").DocumentListResponse>("/documents"),

  getDocument: (id: string) =>
    request<import("@/lib/types/api").DocumentDetail>(`/documents/${id}`),

  deleteDocument: (id: string) =>
    request<import("@/lib/types/api").DeleteResponse>(`/documents/${id}`, {
      method: "DELETE",
    }),
};
