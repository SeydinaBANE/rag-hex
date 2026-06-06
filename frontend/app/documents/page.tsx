"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api/client";
import type { IngestResponse } from "@/lib/types/api";

export default function DocumentsPage() {
  const [files, setFiles] = useState<{ name: string; status: string }[]>([]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const content = await file.text();
    setFiles((prev) => [...prev, { name: file.name, status: "en cours..." }]);

    try {
      await api.ingest({
        document_id: file.name,
        content,
        metadata: { filename: file.name },
      });
      setFiles((prev) =>
        prev.map((f) => (f.name === file.name ? { ...f, status: "indexé" } : f)),
      );
    } catch {
      setFiles((prev) =>
        prev.map((f) => (f.name === file.name ? { ...f, status: "erreur" } : f)),
      );
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Documents</h1>
        <label className="cursor-pointer">
          <Button variant="primary" asChild>
            <span>+ Upload</span>
          </Button>
          <input
            type="file"
            className="hidden"
            accept=".txt,.md,.pdf"
            onChange={handleUpload}
          />
        </label>
      </div>

      <div className="border border-[var(--border)] rounded-lg divide-y divide-[var(--border)]">
        {files.length === 0 && (
          <p className="p-4 text-sm text-[var(--muted-foreground)]">
            Aucun document indexé
          </p>
        )}
        {files.map((f) => (
          <div key={f.name} className="flex items-center justify-between p-4 text-sm">
            <span>{f.name}</span>
            <span
              className={
                f.status === "indexé"
                  ? "text-green-600"
                  : f.status === "erreur"
                    ? "text-red-500"
                    : "text-[var(--muted-foreground)]"
              }
            >
              {f.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
