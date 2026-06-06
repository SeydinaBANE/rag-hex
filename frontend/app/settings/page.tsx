"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function SettingsPage() {
  const [topK, setTopK] = useState(5);

  return (
    <div className="p-6 space-y-6 max-w-lg">
      <h1 className="text-2xl font-bold">Paramètres</h1>

      <div className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">
            Nombre de résultats (top_k)
          </label>
          <Input
            type="number"
            min={1}
            max={50}
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Modèle LLM</label>
          <Input
            value={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}
            disabled
          />
          <p className="text-xs text-[var(--muted-foreground)]">
            Configuré côté serveur via les variables d&apos;environnement
          </p>
        </div>

        <Button variant="primary">Sauvegarder</Button>
      </div>
    </div>
  );
}
