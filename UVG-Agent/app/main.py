# app/main.py
import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import AskBody
from .agent import ask_agent
from .config import CLAUDE_MODEL, KB

app = FastAPI(title="Jack AI – Backend")

# CORS: admite varios orígenes separados por coma en FRONT_ORIGIN
FRONT_ORIGIN = os.getenv(
    "FRONT_ORIGIN",
    "http://localhost:5173,http://127.0.0.1:5173"  # ⬅️ ambos
)
origins = [o.strip() for o in FRONT_ORIGIN.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(body: AskBody):
    try:
        q = (body.query or "").strip()
        if not q:
            raise HTTPException(status_code=422, detail="El campo 'query' es requerido.")

        result = ask_agent(
            q,
            size=body.size or 30,
            max_chunks=body.max_chunks or 20,
            use_semantic=True if body.use_semantic is None else body.use_semantic,
            min_score=body.min_score or 0.0,
        )

        return {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "model": CLAUDE_MODEL,
            "nuclia_kb": KB,
            "params": {
                "size": body.size or 30,
                "max_chunks": body.max_chunks or 20,
                "use_semantic": True if body.use_semantic is None else body.use_semantic,
                "min_score": body.min_score or 0.0,
            },
        }

    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", 502)
        detail = (getattr(e.response, "text", "") or str(e))[:800]
        raise HTTPException(status_code=502, detail=f"Error consultando Nuclia ({status}): {detail}")

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error llamando a Claude: {e}")

