from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class ImproveRequest(BaseModel):
    content: str
    content_type: str
    context: Optional[Dict[str, Any]] = None

class ValidationRequest(BaseModel):
    content: str
    validation_type: str
    criteria: Optional[Dict[str, Any]] = None

class DocumentRequest(BaseModel):
    content: str
    template_type: str
    metadata: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 10

# app/models/response_models.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ChatResponse(BaseModel):
    status: str
    message: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ImproveResponse(BaseModel):
    status: str
    improved_content: str
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class ValidationResponse(BaseModel):
    status: str
    is_valid: bool
    feedback: List[str]
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    status: str
    document: str
    metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    status: str
    results: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[Dict[str, Any]] = None