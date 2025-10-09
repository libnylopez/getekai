import React from "react";
import { motion } from "framer-motion";

export type SourceDoc = {
  id: string;
  title: string;
  url?: string;
  type?: "pdf" | "link" | "file";
  snippet?: string;
};

export default function SourceCard({ s }: { s: SourceDoc }) {
  const Icon = (
    <svg className="h-5 w-5 text-emerald-400" viewBox="0 0 24 24" fill="none" aria-hidden>
      {s.type === "pdf" ? (
        <path d="M6 2h7l5 5v15a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" stroke="currentColor" strokeWidth="1.5" />
      ) : (
        <path d="M10 13a5 5 0 0 1 7-7l2 2a5 5 0 0 1-7 7m-3 1a5 5 0 0 1-7-7l2-2a5 5 0 0 1 7 7" stroke="currentColor" strokeWidth="1.5" />
      )}
    </svg>
  );

  return (
    <motion.a
      href={s.url || "#"}
      target={s.url ? "_blank" : undefined}
      rel={s.url ? "noreferrer" : undefined}
      className="group rounded-2xl border border-white/10 p-4 bg-white/5"
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{Icon}</div>
        <div className="min-w-0">
          <div className="truncate font-medium text-white group-hover:text-emerald-300">
            {s.title}
          </div>
          {s.snippet && (
            <div className="mt-1 text-sm text-white/70 overflow-hidden max-h-12">
              {s.snippet}
            </div>
          )}
        </div>
      </div>
    </motion.a>
  );
}
