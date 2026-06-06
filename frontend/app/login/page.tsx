"use client";

import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    const form = new FormData(e.currentTarget);
    const result = await signIn("credentials", {
      username: form.get("username") as string,
      password: form.get("password") as string,
      redirect: false,
    });

    if (result?.error) {
      setError("Identifiant ou mot de passe incorrect");
    } else {
      router.push("/chat");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--muted)]">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm bg-[var(--background)] p-8 rounded-lg border border-[var(--border)] space-y-4"
      >
        <h1 className="text-xl font-bold text-center">RAG Hex</h1>
        <p className="text-sm text-center text-[var(--muted-foreground)]">
          Connectez-vous pour accéder à l&apos;application
        </p>

        {error && <p className="text-sm text-red-500 text-center">{error}</p>}

        <div className="space-y-2">
          <label htmlFor="username" className="text-sm font-medium">
            Identifiant
          </label>
          <Input id="username" name="username" required autoFocus />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium">
            Mot de passe
          </label>
          <Input id="password" name="password" type="password" required />
        </div>

        <Button type="submit" className="w-full">
          Connexion
        </Button>
      </form>
    </div>
  );
}
