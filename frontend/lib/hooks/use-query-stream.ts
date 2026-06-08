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

  const startStream = useCallback(
    async (text: string, topK = 5): Promise<string> => {
      const controller = new AbortController();
      abortRef.current = controller;
      setIsStreaming(true);
      setTokens([]);

      const accumulated: string[] = [];

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

        if (!response.ok) {
          const errText = await response.text();
          throw new Error(errText || `HTTP ${response.status}`);
        }

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
              return accumulated.join("");
            }
            try {
              const event: StreamEvent = JSON.parse(payload);
              const token = event.data;
              if (event.type === "token" && token) {
                accumulated.push(token);
                setTokens((prev) => [...prev, token]);
              }
            } catch {
              // skip malformed events
            }
          }
        }
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          const errToken = `Erreur : ${(err as Error).message}`;
          accumulated.push(errToken);
          setTokens((prev) => [...prev, errToken]);
        }
      } finally {
        setIsStreaming(false);
      }

      return accumulated.join("");
    },
    [],
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return { tokens, isStreaming, startStream, cancel, answer: tokens.join("") };
}
