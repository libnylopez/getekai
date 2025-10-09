import React from "react";
import type { SourceDoc } from "./SourceCard";
import SourceCard from "./SourceCard";
import { motion } from "framer-motion";

export type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  sources?: SourceDoc[];
};

export default function ChatMessage({ m }: { m: Message }) {
  const isAssistant = m.role === "assistant";

  return (
    <div className={`w-full flex ${isAssistant ? "justify-start" : "justify-end"}`}>
      <motion.div
        className="max-w-[720px] w-full"
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
      >
        <div
          className={[
            "rounded-2xl px-5 py-4 border backdrop-blur transition",
            isAssistant
              ? "bg-white/5 border-white/10"
              : "bg-emerald-600/15 border-emerald-500/20"
          ].join(" ")}
        >
          <div className="text-white/90 leading-relaxed whitespace-pre-wrap">
            {m.text}
          </div>
        </div>

        {isAssistant && m.sources && m.sources.length > 0 && (
          <div className="mt-3 grid grid-cols-1 gap-3">
            {m.sources.map((s) => (
              <SourceCard key={s.id} s={s} />
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}
