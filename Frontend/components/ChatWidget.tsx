"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, Send, User } from "lucide-react";

interface Message {
  role: "user" | "ia";
  texto: string;
}

export default function ChatWidget({
  initialHistory,
  lawTitle,
}: {
  initialHistory: Message[];
  lawTitle: string;
}) {
  const [messages, setMessages] = useState<Message[]>(initialHistory);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend() {
    const trimmed = input.trim();
    if (!trimmed) return;
    setMessages((prev) => [
      ...prev,
      { role: "user", texto: trimmed },
      {
        role: "ia",
        texto:
          "Esta función estará disponible próximamente. Estamos integrando nuestra IA para analizar \"" +
          lawTitle +
          "\" y responder tus preguntas en tiempo real.",
      },
    ]);
    setInput("");
  }

  return (
    <section
      className="rounded-2xl border overflow-hidden"
      style={{ borderColor: "var(--border)", backgroundColor: "var(--bg-card)" }}
    >
      {/* Header */}
      <div
        className="flex items-center gap-3 px-5 py-4 border-b"
        style={{ borderColor: "var(--border)" }}
      >
        <div className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-600">
          <Bot size={16} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
            IA Legislativa
          </p>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
            Análisis contextual basado en el texto oficial de la ley
          </p>
        </div>
        <span className="ml-auto flex items-center gap-1.5 text-xs text-green-400">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          Demo
        </span>
      </div>

      {/* Message history */}
      <div
        className="flex flex-col gap-4 px-5 py-5 overflow-y-auto"
        style={{ minHeight: "260px", maxHeight: "380px" }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
          >
            {/* Avatar */}
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === "ia" ? "bg-blue-600" : "bg-slate-600"
              }`}
            >
              {msg.role === "ia" ? (
                <Bot size={14} className="text-white" />
              ) : (
                <User size={14} className="text-white" />
              )}
            </div>
            {/* Bubble */}
            <div
              className={`max-w-[78%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                msg.role === "user" ? "rounded-tr-sm" : "rounded-tl-sm"
              }`}
              style={{
                backgroundColor:
                  msg.role === "ia"
                    ? "rgba(59,130,246,0.1)"
                    : "rgba(148,163,184,0.1)",
                color: "var(--text-primary)",
              }}
            >
              {msg.texto}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div
        className="flex items-center gap-3 px-4 py-3 border-t"
        style={{ borderColor: "var(--border)" }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={`Pregúntale a nuestra IA sobre "${lawTitle}"…`}
          className="flex-1 bg-transparent text-sm outline-none placeholder:text-slate-500"
          style={{ color: "var(--text-primary)" }}
        />
        <button
          onClick={handleSend}
          className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-600 hover:bg-blue-500 transition-colors disabled:opacity-40"
          disabled={!input.trim()}
        >
          <Send size={14} className="text-white" />
        </button>
      </div>
    </section>
  );
}
