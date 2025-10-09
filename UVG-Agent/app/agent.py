from .llm import preprocess_query
from .nuclia import nuclia_search, build_context
from .clients import client
from .config import CLAUDE_MODEL, INSTRUCTIONS

# ── Orquestación mejorada
def ask_agent(
    question: str, 
    *, 
    size: int = 30, 
    max_chunks: int = 20,
    use_semantic: bool = True,
    min_score: float = 0.0
) -> dict:
    """
    Orquesta el pipeline RAG completo con mejoras.
    
    Args:
        question: Pregunta del usuario
        size: Resultados a obtener de Nuclia
        max_chunks: Máximo de párrafos para el contexto
        use_semantic: Si usar búsqueda semántica (además de keyword)
        min_score: Score mínimo para incluir resultados
    
    Returns:
        dict con 'answer', 'sources' y 'search_results'
    """
    # 1. Preprocesar la consulta
    consulta = preprocess_query(question)
    
    # 2. Búsqueda híbrida (keyword + semantic)
    features = ["keyword"]
    if use_semantic:
        features.append("semantic")
    
    search = nuclia_search(
        consulta, 
        size=size,
        features=features,
        min_score=min_score
    )
    
    # 3. Construir contexto con metadata
    context = build_context(
        search, 
        max_chunks=max_chunks,
        include_metadata=True,
        score_threshold=min_score
    )

    # 4. Generar respuesta con Claude
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=800,
        temperature=0.2,
        system=INSTRUCTIONS,
        messages=[{"role": "user", "content": f"Pregunta: {question}\n\nContexto:\n{context}"}],
    )
    parts = response.content or []
    answer = "".join(getattr(p, "text", "") for p in parts)
    
    # 5. Extraer información de fuentes para el frontend
    sources_info = extract_sources_info(search, max_chunks, min_score)
    
    return {
        "answer": answer,
        "sources": sources_info,
        "search_results": search  # Resultados completos para referencia
    }


def extract_sources_info(search_json: dict, max_chunks: int = 20, score_threshold: float = 0.0) -> list:
    """
    Extrae información estructurada de las fuentes para mostrar en el frontend.
    
    Returns:
        Lista de diccionarios con información de cada fuente
    """
    para = (search_json.get("paragraphs") or {}).get("results", [])
    resources = (search_json.get("resources") or {})
    sources = []
    
    for idx, hit in enumerate(para[:max_chunks]):
        score = hit.get("score", 0.0)
        if score < score_threshold:
            continue
            
        text = (hit.get("text") or "").strip()
        if not text:
            continue
        
        resource_id = hit.get("rid", "")
        field = hit.get("field", "")
        
        # Información del recurso
        resource_info = resources.get(resource_id, {})
        title = resource_info.get("title", "Documento sin título")
        
        # Obtener URL del documento original (múltiples fuentes)
        url = ""
        
        # 1. Intentar obtener de origin.url (para links/web)
        origin = resource_info.get("origin", {})
        if isinstance(origin, dict):
            url = origin.get("url", "") or origin.get("path", "")
        
        # 2. Si no hay URL de origen, intentar metadata
        if not url:
            metadata = resource_info.get("metadata", {})
            if isinstance(metadata, dict):
                url = metadata.get("uri", "") or metadata.get("url", "") or metadata.get("source", "")
        
        # 3. Intentar obtener de otros campos comunes
        if not url:
            url = resource_info.get("link", "") or resource_info.get("uri", "")
        
        # 4. Si es un archivo subido, intentar obtener URL de descarga
        if not url:
            files = resource_info.get("files", {})
            if isinstance(files, dict):
                # Buscar el archivo principal (file o similar)
                for file_key, file_data in files.items():
                    if isinstance(file_data, dict) and file_data.get("uri"):
                        url = file_data.get("uri", "")
                        break
        
        # 5. Si aún no hay URL y tenemos resource_id, construir enlace al recurso en Nuclia
        # Esto permite al menos acceder al recurso en la interfaz de Nuclia
        if not url and resource_id:
            from .config import NUCLIA_API_BASE, KB
            # URL para visualizar/descargar el recurso
            url = f"{NUCLIA_API_BASE}/kb/{KB}/resource/{resource_id}"
        
        # Número de página
        position = hit.get("position", {})
        page_num = position.get("page_number")
        
        # Determinar tipo de URL
        url_type = "none"
        if url:
            if "http://" in url or "https://" in url:
                if "nuclia" in url or "rag.progress.cloud" in url:
                    url_type = "nuclia"  # URL interna de Nuclia
                else:
                    url_type = "external"  # URL externa/original
            else:
                url_type = "resource"  # ID de recurso
        
        # Construir objeto de fuente
        source = {
            "id": idx + 1,
            "title": title,
            "text": text,
            "score": round(score, 3) if score else None,
            "page": page_num,
            "field": field,
            "resource_id": resource_id,
            "url": url,  # URL para abrir el documento
            "url_type": url_type,  # Tipo de URL
            "has_url": bool(url)  # Flag para saber si hay URL disponible
        }
        
        sources.append(source)
    
    return sources
