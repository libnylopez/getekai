import requests
from .config import NUCLIA_API_BASE, KB, HEADERS
from typing import Optional, List, Dict, Any

# ── Búsqueda Nuclia mejorada
def nuclia_search(
    query: str, 
    size: int = 20,
    features: Optional[List[str]] = None,
    filters: Optional[List[str]] = None,
    faceted: Optional[List[str]] = None,
    sort: Optional[str] = None,
    min_score: Optional[float] = None,
    vectorset: str = "multilingual-2024-05-06"
) -> dict:
    """
    Búsqueda mejorada en Nuclia con múltiples opciones.
    
    Args:
        query: Texto a buscar
        size: Número de resultados (default: 20)
        features: Tipos de búsqueda ['keyword', 'semantic', 'relations']
        filters: Filtros como ['/classification.labels/tipo/documento']
        faceted: Campos para facetado ['/classification.labels']
        sort: Ordenamiento ('created', 'modified', 'score')
        min_score: Score mínimo para resultados (0.0-1.0)
        vectorset: Conjunto de vectores para búsqueda semántica
    """
    url = f"{NUCLIA_API_BASE}/kb/{KB}/search"
    
    # Parámetros base
    params: Dict[str, Any] = {
        "query": query,
        "size": size,
    }
    
    # Búsqueda híbrida por defecto (keyword + semantic)
    if features is None:
        features = ["keyword", "semantic"]
    params["features"] = features
    
    # Vectorset para búsqueda semántica
    if "semantic" in features:
        params["vectorset"] = vectorset
    
    # Filtros opcionales
    if filters:
        params["filters"] = filters
    
    # Facetado
    if faceted:
        params["faceted"] = faceted
    
    # Ordenamiento
    if sort:
        params["sort"] = sort
    
    # Score mínimo
    if min_score is not None:
        params["min_score"] = min_score
    
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

# ── Construcción de contexto mejorada
def build_context(
    search_json: dict, 
    max_chunks: int = 20,
    include_metadata: bool = True,
    score_threshold: float = 0.0
) -> str:
    """
    Construye contexto desde resultados de búsqueda con mejoras.
    
    Args:
        search_json: JSON de respuesta de nuclia_search
        max_chunks: Máximo de párrafos a incluir
        include_metadata: Si incluir título/fuente del documento
        score_threshold: Score mínimo para incluir un resultado (0.0-1.0)
    """
    para = (search_json.get("paragraphs") or {}).get("results", [])
    resources = (search_json.get("resources") or {})  # Información de archivos
    blocks = []
    
    for hit in para[:max_chunks]:
        # Verificar score si está disponible
        score = hit.get("score", 1.0)
        if score < score_threshold:
            continue
            
        text = (hit.get("text") or "").strip()
        if not text:
            continue
        
        # Agregar metadata si se solicita
        if include_metadata:
            resource_id = hit.get("rid", "")
            field = hit.get("field", "")
            
            # Intentar obtener información del archivo/recurso
            resource_info = resources.get(resource_id, {})
            title = resource_info.get("title", "")
            
            # Obtener número de página si está disponible
            position = hit.get("position", {})
            page_num = position.get("page_number")
            
            # Crear encabezado enriquecido con metadata
            metadata_parts = []
            if title:
                metadata_parts.append(f"📄 {title}")
            elif field:
                metadata_parts.append(f"Fuente: {field}")
            
            if page_num:
                metadata_parts.append(f"(página {page_num})")
            
            if metadata_parts:
                metadata_header = "[" + " ".join(metadata_parts) + "]\n"
                blocks.append(f"{metadata_header}{text}")
            else:
                blocks.append(text)
        else:
            blocks.append(text)
    
    return "\n\n---\n\n".join(blocks)  # Separador más visible

