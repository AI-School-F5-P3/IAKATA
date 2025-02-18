from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class Message(BaseModel):
    id: UUID
    session_id: UUID
    role: str  # 'user' o 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    id: UUID
    user_id: str
    board_id: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime
    last_updated: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: Message
    context_used: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None