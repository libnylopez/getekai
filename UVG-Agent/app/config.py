# app/config.py
import os
from dataclasses import dataclass
from typing import Optional

# Carga .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def _clean(s: Optional[str]) -> str:
    return (s or "").strip().strip('"').strip("'")

# ---------------- System Prompt por defecto (UVG) ----------------
DEFAULT_INSTRUCTIONS = """
Eres “Jack”, asistente especializado en la Universidad del Valle de Guatemala (UVG).
OBJETIVO: Ayudar a personas interesadas en la UVG (admisiones, carreras, sedes, costos, becas, reglamentos, servicios, calendario, contactos), priorizando SIEMPRE fuentes oficiales de UVG o los fragmentos (RAG) provistos.

ALCANCE Y CONDUCTA:
- Responde preguntas UVG con precisión y cita fuentes si hay RAG.
- Si el usuario saluda o hace small talk (“hola”, “¿cómo estás?”, “buenas”), responde cordial (1–2 líneas) y de inmediato ofrece ayuda en temas UVG (2–4 opciones: admisiones, carreras, costos/becas, calendario, recursos del campus). No digas “no encuentro información en el contexto” en esos casos.
- Si la consulta es ambigua/incompleta, pide un dato clave (sede, carrera, programa) pero da guía inicial útil.
- Si el tema es fuera de UVG, responde breve y redirige a recursos externos; luego sugiere volver a temas UVG.

POLÍTICA DE FUENTES (RAG):
- Prioriza uvg.edu.gt, subdominios y documentos institucionales.
- Cita al final como “Fuentes consultadas:” con título y URL/ID. Si no hubo RAG, puedes omitir la sección.

FORMATO:
- Para respuestas informativas UVG usa este esquema cuando aplique:
  # Respuesta
  (1–3 líneas con lo principal)

  ## Detalles
  - puntos clave

  ## Siguientes pasos
  1) …

  ## Fuentes consultadas
  - Título (URL o ID)
- Para saludos/small talk: manténlo breve (sin forzar el esquema completo).

RESTRICCIONES:
- No inventes costos/fechas.
- No des diagnósticos médicos/legales.
- Indica si falta certeza y sugiere validar con Admisiones/Registro/Finanzas/Facultad.

IDIOMA:
- Responde en el idioma del usuario (por defecto español, Guatemala).
""".strip()

# ---------------- Settings ----------------
@dataclass
class Settings:
    # === Nuclia (RAG)
    NUCLIA_API_BASE: str = _clean(os.getenv("NUCLIA_API_BASE"))
    KB: str = _clean(os.getenv("KB"))
    NUCLIA_TOKEN: str = _clean(os.getenv("NUCLIA_TOKEN"))

    # === Anthropic (LLM)
    ANTHROPIC_KEY: str = _clean(os.getenv("ANTHROPIC_KEY"))
    CLAUDE_MODEL: str = _clean(os.getenv("CLAUDE_MODEL") or "claude-3-5-sonnet-latest")

    # === Frontends permitidos (CORS)
    FRONT_ORIGIN: str = _clean(os.getenv("FRONT_ORIGIN") or "http://localhost:5173,http://127.0.0.1:5173")

    # === Prompt principal
    INSTRUCTIONS: str = _clean(os.getenv("INSTRUCTIONS")) or DEFAULT_INSTRUCTIONS

    # === Parámetros LLM recomendados
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS") or 900)
    TEMPERATURE: float = float(os.getenv("TEMPERATURE") or 0.2)

settings = Settings()

# ---------------- Re-exports convenientes ----------------
NUCLIA_API_BASE = settings.NUCLIA_API_BASE
KB = settings.KB
NUCLIA_TOKEN = settings.NUCLIA_TOKEN

ANTHROPIC_KEY = settings.ANTHROPIC_KEY
CLAUDE_MODEL = settings.CLAUDE_MODEL

FRONT_ORIGIN = settings.FRONT_ORIGIN
INSTRUCTIONS = settings.INSTRUCTIONS

MAX_TOKENS = settings.MAX_TOKENS
TEMPERATURE = settings.TEMPERATURE

# ---------------- Cabeceras para Nuclia (lo espera nuclia.py) ----------------
# ---------------- Cabeceras para Nuclia (auto Cloud/OSS) ----------------
def _build_nuclia_headers() -> dict:
    """
    Nuclia Cloud (RAG-as-a-Service, p.ej. rag.progress.cloud):
      - Usa x-api-key: <token>
    Nuclia OSS / NucliaDB / otros:
      - Usa Authorization: Bearer <token>
    """
    base = (NUCLIA_API_BASE or "").lower()
    token = NUCLIA_TOKEN or ""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if "rag.progress.cloud" in base or "nuclia.cloud" in base:
        # Cloud
        headers["x-api-key"] = token
    else:
        # OSS / NucliaDB
        headers["Authorization"] = f"Bearer {token}"

    return headers

HEADERS = _build_nuclia_headers()

