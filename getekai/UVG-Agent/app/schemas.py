from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# ── Esquemas mejorados
class AskBody(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    size: Optional[int] = Field(default=30, ge=1, le=100)        # cuántos resultados pedir a Nuclia
    max_chunks: Optional[int] = Field(default=20, ge=1, le=50)   # cuántos párrafos meter al contexto
    use_semantic: Optional[bool] = Field(default=True)           # búsqueda semántica + keyword
    min_score: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)  # score mínimo
