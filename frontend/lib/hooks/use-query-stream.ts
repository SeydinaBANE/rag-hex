"use client";

import { useCallback, useRef, useState } from "react";

interface StreamEvent {
  type: "token" | "done" | "error";
  data?: string;
}

export function useQueryStream() {
  const [tokens, setTokens] = useState<string[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const startStream = useCallback(async (text: string, topK = 5) => {
    const controller = new AbortController();
    abortRef.current = controller;
    setIsStreaming(true);
    setTokens([]);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/query/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, top_k: topK }),
          signal: controller.signal,
        },
      );

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = line.slice(6).trim();
          if (payload === "[DONE]") {
            setIsStreaming(false);
            return;
          }
          try {
            const event: StreamEvent = JSON.parse(payload);
            if (event.type === "token" && event.data) {
              setTokens((prev) => [...prev, event.data]);
            }
          } catch {
            // skip malformed events
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setTokens((prev) => [...prev, `Error: ${(err as Error).message}`]);
      }
    } finally {
      setIsStreaming(false);
    }
  }, []);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return { tokens, isStreaming, startStream, cancel, answer: tokens.join("") };
}
