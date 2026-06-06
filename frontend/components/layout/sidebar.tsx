"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/chat", label: "Chat", icon: "💬" },
  { href: "/documents", label: "Documents", icon: "📄" },
  { href: "/settings", label: "Paramètres", icon: "⚙️" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-[var(--border)] h-full flex flex-col bg-[var(--muted)]">
      <div className="p-4 font-bold text-lg border-b border-[var(--border)]">
        RAG Hex
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
              pathname?.startsWith(item.href)
                ? "bg-[var(--border)] font-medium"
                : "hover:bg-[var(--border)]",
            )}
          >
            <span>{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
