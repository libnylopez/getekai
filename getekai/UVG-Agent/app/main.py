# app/main.py
import os
import httpx
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .schemas import AskBody
from .agent import ask_agent
from .nuclia import nuclia_search, build_context
from .config import CLAUDE_MODEL, KB, NUCLIA_API_BASE, HEADERS

app = FastAPI(title="Jack AI – Backend")

# ---- CORS
FRONT_ORIGIN = os.getenv(
    "FRONT_ORIGIN",
    "http://localhost:5173,http://127.0.0.1:5173"
)
ALLOWED = [o.strip() for o in FRONT_ORIGIN.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Health
@app.get("/health")
def health():
    return {"ok": True, "kb": KB}

# ---- Ask (usa tu pipeline existente)
@app.post("/ask")
def ask(body: AskBody):
    try:
        return ask_agent(
            question=body.query,
            size=body.size or 30,
            max_chunks=body.max_chunks or 20,
            use_semantic=True if body.use_semantic is None else body.use_semantic,
            min_score=body.min_score or 0.0,
        )
    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", 502)
        detail = (getattr(e.response, "text", "") or str(e))[:800]
        raise HTTPException(status_code=502, detail=f"Error consultando Nuclia ({status}): {detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")

# ---- (Opcional) Endpoint de búsqueda directa a Nuclia para debug
@app.get("/search")
def search(query: str, size: int = 20, min_score: float = 0.0):
    try:
        data = nuclia_search(query=query, size=size, min_score=min_score)
        # también te regreso un contexto ensamblado por si lo quieres ver
        context = build_context(data, max_chunks=20)
        return {"raw": data, "context": context}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en búsqueda Nuclia: {e}")

# ---- 🔥 Nuevo: proxy/stream del archivo original (PDF u otros)
@app.get("/resources/{rid}/file")
async def resource_file(rid: str):
    """
    Sirve el archivo original del recurso de Nuclia en streaming.
    Esto evita exponer el token en el frontend y pone el Content-Type correcto (application/pdf).
    """
    # Ajusta el path al de "download/original" que use tu tenant (según Nuclia)
    url = f"{NUCLIA_API_BASE}/kb/{KB}/resource/{rid}/file/original"
    headers = {**HEADERS}  # HEADERS = {"x-api-key": "<token>"}
    timeout = httpx.Timeout(60.0, connect=20.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(url, headers=headers)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)

        media_type = r.headers.get("content-type", "application/octet-stream")
        # Forzar inline para que el navegador lo pueda mostrar
        dispo = r.headers.get("content-disposition", f'inline; filename="{rid}.pdf"')

        return StreamingResponse(
            r.aiter_bytes(),
            media_type=media_type,
            headers={"Content-Disposition": dispo},
        )
