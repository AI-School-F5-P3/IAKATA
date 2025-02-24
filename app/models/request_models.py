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