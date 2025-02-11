from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class ResponseType(Enum):
    CHAT = "chat"
    VALIDATION = "validation"
    SUGGESTION = "suggestion"
    DOCUMENTATION = "documentation"

class LLMRequest(BaseModel):
    query: str
    context: Optional[Dict] = None
    response_type: ResponseType
    temperature: Optional[float] = None
    language: Optional[str] = "es"

class LLMResponse(BaseModel):
    content: str
    metadata: Optional[Dict] = None
    confidence: Optional[float] = None
    suggestions: Optional[List[str]] = None
    validation_results: Optional[Dict[str, bool]] = None