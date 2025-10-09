import React from "react";

export type BackendStatus = "online" | "offline" | "checking";

export default function Header({ status }: { status: BackendStatus }) {
  const dot =
    status === "online"
      ? "bg-emerald-500"
      : status === "checking"
      ? "bg-amber-400"
      : "bg-rose-500";

  return (
    <div className="sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-black/20 bg-black/30 border-b border-white/10">
      <div className="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
        {/* Izquierda vacía (se pidió eliminar la marca) */}
        <div aria-hidden className="h-6" />
        {/* Sólo status a la derecha */}
        <div className="flex items-center gap-2 text-sm text-white/70">
          <span className={`inline-flex h-2.5 w-2.5 rounded-full ${dot}`} />
          <span>Backend: {status[0].toUpperCase() + status.slice(1)}</span>
        </div>
      </div>
    </div>
  );
}

