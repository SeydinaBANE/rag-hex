"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api/client";
import type { DocumentDetail } from "@/lib/types/api";

export default function DocumentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getDocument(id)
      .then(setDoc)
      .catch(() => setError("Document introuvable"))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleDelete() {
    if (!confirm("Supprimer ce document ?")) return;
    try {
      await api.deleteDocument(id);
      router.push("/documents");
    } catch {
      setError("Erreur lors de la suppression");
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-[var(--muted-foreground)]">Chargement...</p>
      </div>
    );
  }

  if (error || !doc) {
    return (
      <div className="p-6 space-y-4">
        <p className="text-red-500">{error ?? "Document introuvable"}</p>
        <Link href="/documents">
          <Button variant="outline">&larr; Retour aux documents</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <Link
            href="/documents"
            className="text-sm text-[var(--muted-foreground)] hover:underline"
          >
            &larr; Retour
          </Link>
          <h1 className="text-2xl font-bold mt-1">{doc.id}</h1>
        </div>
        <Button variant="outline" onClick={handleDelete}>
          Supprimer
        </Button>
      </div>

      <div className="border border-[var(--border)] rounded-lg p-4 space-y-2">
        <h2 className="text-sm font-semibold text-[var(--muted-foreground)]">
          Metadata
        </h2>
        {Object.keys(doc.metadata).length === 0 ? (
          <p className="text-sm text-[var(--muted-foreground)]">
            Aucune metadata
          </p>
        ) : (
          <dl className="space-y-1 text-sm">
            {Object.entries(doc.metadata).map(([key, value]) => (
              <div key={key} className="flex gap-2">
                <dt className="font-medium min-w-24">{key}</dt>
                <dd className="text-[var(--muted-foreground)]">{value}</dd>
              </div>
            ))}
          </dl>
        )}
      </div>

      <div className="border border-[var(--border)] rounded-lg p-4 space-y-2">
        <h2 className="text-sm font-semibold text-[var(--muted-foreground)]">
          Contenu
        </h2>
        <pre className="text-sm whitespace-pre-wrap font-sans">
          {doc.content}
        </pre>
      </div>

      <div className="space-y-2">
        <h2 className="text-sm font-semibold text-[var(--muted-foreground)]">
          Chunks ({doc.chunks.length})
        </h2>
        {doc.chunks.map((chunk) => (
          <div
            key={chunk.chunk_id}
            className="border border-[var(--border)] rounded-lg p-3 space-y-1"
          >
            <div className="text-xs text-[var(--muted-foreground)] flex gap-4">
              <span>Position {chunk.position}</span>
              {chunk.page != null && <span>Page {chunk.page}</span>}
              <span className="font-mono">{chunk.chunk_id.slice(0, 16)}</span>
            </div>
            <p className="text-sm whitespace-pre-wrap">{chunk.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
