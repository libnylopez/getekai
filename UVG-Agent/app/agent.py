# app/agent.py
from __future__ import annotations
import re
from typing import Literal, Tuple

from .llm import preprocess_query
from .nuclia import nuclia_search, build_context
from .clients import client
from .config import CLAUDE_MODEL, INSTRUCTIONS, MAX_TOKENS, TEMPERATURE

Intent = Literal["greeting", "uvg", "offtopic", "unknown"]

# --- Heurística rápida para detectar saludos ---
_GREET_RE = re.compile(r"\b(hola|buen[oa]s|qué tal|como estas|¿cómo estás|hi|hello)\b", re.I)

def classify_intent(question: str) -> Intent:
    q = (question or "").strip().lower()
    if not q:
        return "unknown"
    if _GREET_RE.search(q) and len(q.split()) <= 8:
        return "greeting"
    # Heurística UVG mínima (menciona carreras, admisiones, sedes, etc.)
    uvgtokens = [
        "uvg", "altiplano", "campus sur", "campus central", "admisiones",
        "carrera", "inscripción", "beca", "arancel", "pensum", "malla",
        "calendario", "facultad", "laboratorio", "crea", "makerspace"
    ]
    if any(t in q for t in uvgtokens):
        return "uvg"
    # Dejar lo demás en unknown; el RAG puede decidir luego
    return "unknown"

def smalltalk_reply() -> str:
    # Respuesta cordial breve + oferta de ayuda UVG
    return (
        "¡Hola! 😊 ¿En qué puedo apoyarte de la UVG?\n\n"
        "**Puedo ayudarte con:**\n"
        "- Admisiones y requisitos\n"
        "- Carreras y planes de estudio\n"
        "- Costos, becas y formas de pago\n"
        "- Calendario académico y fechas clave\n"
        "- Recursos del campus (biblioteca, MakerSpace, laboratorios)\n\n"
        "Cuéntame qué sede o programa te interesa y avanzamos."
    )

# ── Orquestación con detección de intención + self-check
def ask_agent(
    question: str,
    *,
    size: int = 30,
    max_chunks: int = 20,
    use_semantic: bool = True,
    min_score: float = 0.0
) -> dict:
    if not question or not question.strip():
        return {
            "answer": "¡Hola! ¿Qué te gustaría saber de la UVG? Puedo ayudarte con admisiones, carreras, costos, becas y más.",
            "sources": [],
            "search_results": {},
        }

    intent = classify_intent(question)

    # --- Caso 1: Saludos / small talk (no dependas de RAG) ---
    if intent == "greeting":
        return {
            "answer": smalltalk_reply(),
            "sources": [],
            "search_results": {},
        }

    # --- Caso 2: Consulta UVG (o desconocida que intentamos resolver con RAG) ---
    consulta = preprocess_query(question.strip())

    features = ["keyword"]
    if use_semantic:
        features.append("semantic")

    search = nuclia_search(
        consulta,
        size=size,
        features=features,
        min_score=min_score,
    )

    # Construir contexto
    context = build_context(
        search,
        max_chunks=max_chunks,
        include_metadata=True,
        score_threshold=min_score,
    )

    # Si no hay contexto útil, no devolvamos “no encuentro”; guiemos al usuario
    no_context = not context or context.strip() == ""

    # Prompt usuario principal
    user_prompt = (
        f"Pregunta: {question}\n\n"
        f"Contexto (fragmentos UVG):\n{context if not no_context else '(sin pasajes relevantes)'}\n\n"
        "Si el contexto es limitado o nulo, responde igual con una guía breve y solicita datos clave "
        "(sede, carrera, programa), sin inventar. Si aplica, sigue el esquema Markdown."
    )

    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=INSTRUCTIONS,
        messages=[{"role": "user", "content": user_prompt}],
    )

    parts = resp.content or []
    answer = "".join(getattr(p, "text", "") for p in parts).strip()

    # Self-check: si parece respuesta informativa pero no trae secciones, reformatea
    def _needs_fix(txt: str) -> bool:
        if not txt:
            return False
        # Si contiene bullets y bloques, bien; si no, intenta estructurar
        headers = ["# Respuesta", "## Detalles", "## Siguientes pasos"]
        return any(kw in question.lower() for kw in ["requisito", "costo", "beca", "calendario", "plan", "malla", "proceso"]) and not all(h in txt for h in headers)

    if _needs_fix(answer):
        fix_prompt = (
            "Reestructura estrictamente en el siguiente esquema Markdown, sin texto fuera del esquema:\n\n"
            "# Respuesta\n(1–3 líneas)\n\n"
            "## Detalles\n- puntos clave\n\n"
            "## Siguientes pasos\n1) …\n\n"
            "## Fuentes consultadas\n- Título (URL o ID)\n\n"
            f"=== TEXTO ===\n{answer}"
        )
        fix = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=min(600, MAX_TOKENS),
            temperature=0.0,
            system="Eres un reformateador estricto de Markdown.",
            messages=[{"role": "user", "content": fix_prompt}],
        )
        answer2 = "".join(getattr(p, "text", "") for p in (fix.content or [])).strip()
        if answer2:
            answer = answer2

    # Fuentes para el frontend
    sources_info = extract_sources_info(search, max_chunks=max_chunks, score_threshold=min_score)

    # Si no hubo contexto y la respuesta sigue siendo pobre, ofrece guía UVG
    if no_context and (not answer or len(answer) < 20):
        answer = (
            "Puedo ayudarte con información de la UVG aunque no encontré pasajes relevantes ahora mismo.\n\n"
            "**Dime:** sede (Altiplano, Central, Sur) y programa/carrera que te interesa.\n\n"
            "**Temas comunes:** admisiones, requisitos, costos/becas, calendario, laboratorios, servicios del campus."
        )

    return {
        "answer": answer,
        "sources": sources_info,
        "search_results": search,
    }

def extract_sources_info(
    search_json: dict,
    max_chunks: int = 20,
    score_threshold: float = 0.0
) -> list:
    para = (search_json.get("paragraphs") or {}).get("results", [])
    resources = (search_json.get("resources") or {})
    sources = []

    for idx, hit in enumerate(para[:max_chunks]):
        score = hit.get("score", 0.0)
        if score_threshold and score < score_threshold:
            continue

        text = (hit.get("text") or "").strip()
        if not text:
            continue

        resource_id = hit.get("rid", "") or hit.get("resource", "")
        field = hit.get("field", "")

        resource_info = resources.get(resource_id, {}) if isinstance(resources, dict) else {}
        title = resource_info.get("title") or "Documento sin título"

        url = ""
        origin = resource_info.get("origin", {})
        if isinstance(origin, dict):
            url = origin.get("url", "") or origin.get("path", "")

        if not url:
            metadata = resource_info.get("metadata", {})
            if isinstance(metadata, dict):
                url = metadata.get("uri", "") or metadata.get("url", "") or metadata.get("source", "")

        if not url:
            url = resource_info.get("link", "") or resource_info.get("uri", "")

        if not url:
            files = resource_info.get("files", {})
            if isinstance(files, dict):
                for _k, file_data in files.items():
                    if isinstance(file_data, dict) and file_data.get("uri"):
                        url = file_data.get("uri", "")
                        break

        if not url and resource_id:
            from .config import NUCLIA_API_BASE, KB
            url = f"{NUCLIA_API_BASE}/kb/{KB}/resource/{resource_id}"

        position = hit.get("position", {}) or {}
        page_num = position.get("page_number")

        url_type = "none"
        if url:
            if url.startswith("http://") or url.startswith("https://"):
                url_type = "nuclia" if "nuclia" in url or "rag.progress.cloud" in url else "external"
            else:
                url_type = "resource"

        sources.append({
            "id": idx + 1,
            "title": title,
            "text": text,
            "score": round(score, 3) if isinstance(score, (int, float)) else None,
            "page": page_num,
            "field": field,
            "resource_id": resource_id,
            "url": url,
            "url_type": url_type,
            "has_url": bool(url),
        })

    return sources

