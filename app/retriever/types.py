# app/retriever/types.py
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class SearchStrategy(Enum):
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"

class RelevanceType(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SearchResult(BaseModel):
    """Resultado individual de búsqueda"""
    text: str
    score: float
    metadata: Dict
    section_id: str
    relevance: RelevanceType
    context: Optional[Dict] = None

class SearchRequest(BaseModel):
    """Petición de búsqueda"""
    query: str
    strategy: SearchStrategy = SearchStrategy.HYBRID
    filters: Optional[Dict] = None
    top_k: int = 5
    min_score: float = 0.2

class SearchResponse(BaseModel):
    """Respuesta de búsqueda"""
    results: List[SearchResult]
    metadata: Dict
    total_found: int
    search_strategy: SearchStrategy

class SearchQuery(BaseModel):
    """Consulta de búsqueda"""
    query: str
    filters: Optional[Dict] = None
    top_k: int = 5

class RetrievedContext(BaseModel):
    """Contexto recuperado"""
    text: str
    metadata: Dict