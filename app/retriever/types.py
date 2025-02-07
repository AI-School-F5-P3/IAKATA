from pydantic import BaseModel
from typing import List, Dict, Optional

class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict] = None
    top_k: int = 5

class RetrievedContext(BaseModel):
    content: str
    relevance_score: float
    source: str
    metadata: Optional[Dict] = None

class SearchResult(BaseModel):
    query: str
    contexts: List[RetrievedContext]
    total_results: int