from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from core.llm.types import ResponseType

class BoardSection(BaseModel):
    """Representa el contenido a procesar del tablero Lean Kata"""
    content: str
    metadata: Dict[str, str]
    additional_context: Optional[Dict[str, Any]] = None

class SearchQuery(BaseModel):
    """Consulta de búsqueda"""
    text: str
    metadata: Dict[str, str]
    max_results: int = 5
    filters: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    """Resultado de búsqueda"""
    id: str
    text: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class RankingConfig(BaseModel):
    """Configuración para el ranking de resultados"""
    base_threshold: float = 0.2
    keyword_boost: float = 0.3
    type_boost: float = 0.4
    max_score: float = 1.0

class FilterConfig(BaseModel):
    """Configuración para el filtrado de resultados"""
    min_score: float = 0.6
    max_results: int = 5
    required_metadata: Optional[List[str]] = None

class RetrieverResponse(BaseModel):
    """Respuesta del sistema retriever"""
    response_type: ResponseType
    search_results: List[Dict[str, Any]]
    suggestions: Optional[List[str]] = None
    validation_criteria: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None