import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

type Props = {
  onAsk: (q: string, endpoint: string) => void;
  loading: boolean;
  endpoints?: string[];
  variant?: "composer" | "panel";
};

export default function AskBox({
  onAsk,
  loading,
  endpoints = ["/ask"],
  variant = "composer",
}: Props) {
  const [q, setQ] = useState("");
  const [ep, setEp] = useState(endpoints[0] || "/ask");
  const taRef = useRef<HTMLTextAreaElement | null>(null);

  // ⌘/Ctrl+K enfoca (sin mostrar tip)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        taRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // autosize
  const autosize = () => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = Math.min(el.scrollHeight, 220) + "px";
  };

  const send = () => {
    if (!q.trim() || loading) return;
    onAsk(q.trim(), ep);
    setQ("");
    requestAnimationFrame(() => {
      autosize();
      taRef.current?.focus();
    });
  };

  const shell =
    variant === "composer"
      ? "rounded-2xl border border-white/10 bg-black/35 backdrop-blur p-3"
      : "rounded-2xl border border-white/10 bg-white/5 p-4";

  return (
    <div className={shell}>
      <div className="flex items-end gap-3">
        {/* textarea */}
        <div className="flex-1 rounded-xl ring-1 ring-white/10 bg-gradient-to-b from-emerald-900/10 to-emerald-600/10 focus-within:ring-emerald-400/30 transition">
          <textarea
            ref={taRef}
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              autosize();
            }}
            onInput={autosize}
            placeholder="Escribe tu pregunta…"
            rows={1}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            className="w-full resize-none bg-transparent outline-none text-white placeholder-white/40 px-4 py-3"
            aria-label="Escribe tu pregunta"
          />
        </div>

        {/* endpoint */}
        <label className="hidden md:inline-flex flex-col text-xs text-white/60">
          <span className="mb-1">Endpoint</span>
          <select
            className="rounded-xl border border-white/10 bg-black/40 text-white px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            value={ep}
            onChange={(e) => setEp(e.target.value)}
          >
            {endpoints.map((v) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
        </label>

        {/* enviar */}
        <motion.button
          whileTap={{ scale: 0.98 }}
          whileHover={!loading && q.trim() ? { scale: 1.02 } : {}}
          onClick={send}
          disabled={!q.trim() || loading}
          className={`shrink-0 inline-flex items-center justify-center rounded-xl px-5 py-3 font-medium transition ${
            !q.trim() || loading
              ? "bg-white/10 text-white/40 cursor-not-allowed"
              : "bg-emerald-600 text-white hover:bg-emerald-700"
          }`}
          aria-label="Preguntar"
        >
          {loading ? "Enviando…" : "Preguntar"}
        </motion.button>
      </div>
    </div>
  );
}

