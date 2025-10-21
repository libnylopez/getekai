from .clients import client
from .config import CLAUDE_MODEL

def preprocess_query(question: str) -> str:
    system_prompt = (
        "Eres un optimizador de consultas experto. Devuelve SOLAMENTE la nueva consulta de búsqueda, "
        "sin explicaciones. Ej: '¿Cómo restauro copia de seguridad?' -> 'restaurar copia seguridad'"
    )
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=60,
        temperature=0.0,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Pregunta original: {question}"}],
    )
    new_query = "".join(getattr(p, "text", "") for p in response.content or []).strip()
    new_query = new_query.strip('"').strip("'")
    return new_query or question
