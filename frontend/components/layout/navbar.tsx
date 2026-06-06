"use client";

import { signOut, useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const { data: session } = useSession();

  return (
    <header className="h-14 border-b border-[var(--border)] flex items-center justify-end px-4 gap-4">
      <span className="text-sm text-[var(--muted-foreground)]">
        {session?.user?.name}
      </span>
      <Button variant="ghost" size="sm" onClick={() => signOut({ callbackUrl: "/login" })}>
        Déconnexion
      </Button>
    </header>
  );
}
