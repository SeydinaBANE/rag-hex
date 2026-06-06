"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api/client";
import type { DocumentSummary } from "@/lib/types/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    api.listDocuments().then((res) => setDocuments(res.documents));
  }, []);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const content = await file.text();

    try {
      await api.ingest({
        document_id: file.name,
        content,
        metadata: { filename: file.name },
      });
      const res = await api.listDocuments();
      setDocuments(res.documents);
    } catch {
      /* ignore */
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Documents</h1>
        <label className="cursor-pointer">
          <Button variant="primary" asChild disabled={uploading}>
            <span>{uploading ? "Upload..." : "+ Upload"}</span>
          </Button>
          <input
            type="file"
            className="hidden"
            accept=".txt,.md,.pdf"
            onChange={handleUpload}
            disabled={uploading}
          />
        </label>
      </div>

      <div className="border border-[var(--border)] rounded-lg divide-y divide-[var(--border)]">
        {documents.length === 0 && (
          <p className="p-4 text-sm text-[var(--muted-foreground)]">
            Aucun document indexé
          </p>
        )}
        {documents.map((doc) => (
          <Link
            key={doc.id}
            href={`/documents/${doc.id}`}
            className="flex items-center justify-between p-4 text-sm hover:bg-[var(--muted)] transition-colors"
          >
            <span>{doc.id}</span>
            <span className="text-[var(--muted-foreground)]">
              {doc.chunk_count} chunk{doc.chunk_count !== 1 ? "s" : ""}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
