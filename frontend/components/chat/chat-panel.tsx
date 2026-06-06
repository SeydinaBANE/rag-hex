"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { MessageBubble } from "./message-bubble";
import { useQueryStream } from "@/lib/hooks/use-query-stream";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function ChatPanel() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const { tokens, isStreaming, startStream, cancel } = useQueryStream();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    await startStream(input);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: tokens.join("") },
    ]);
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} content={msg.content} />
        ))}
        {isStreaming && tokens.length > 0 && (
          <MessageBubble role="assistant" content={tokens.join("")} isStreaming />
        )}
        {messages.length === 0 && !isStreaming && (
          <p className="text-center text-[var(--muted-foreground)] mt-20">
            Posez une question à vos documents
          </p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-[var(--border)] p-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Votre question..."
          className="flex-1 h-10 rounded-md border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm focus:outline-none focus:ring-2"
          disabled={isStreaming}
        />
        {isStreaming ? (
          <Button type="button" variant="outline" onClick={cancel}>
            Stop
          </Button>
        ) : (
          <Button type="submit">Envoyer</Button>
        )}
      </form>
    </div>
  );
}
