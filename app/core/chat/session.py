from typing import Dict, Optional, List
from uuid import UUID, uuid4
import logging
from datetime import datetime, timedelta
from .types import ChatSession, Message
from .exceptions import SessionNotFoundError, SessionExpiredError

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, session_timeout: int = 3600):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = session_timeout

    async def get_or_create_session(
        self, 
        session_id: Optional[str] = None,
        user_id: str = "default_user"  # Añadido user_id con valor por defecto
    ) -> ChatSession:
        """Obtiene una sesión existente o crea una nueva"""
        if session_id and session_id in self.sessions:
            try:
                return self.get_session(session_id)
            except (SessionNotFoundError, SessionExpiredError):
                pass
        
        # Crear nueva sesión
        new_session_id = session_id or str(uuid4())
        session = ChatSession(
            id=new_session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            messages=[],
            metadata={}
        )
        self.sessions[new_session_id] = session
        return session

    def get_session(self, session_id: str) -> ChatSession:
        """Obtiene una sesión existente"""
        session = self.sessions.get(session_id)
        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        if self._is_session_expired(session):
            self.close_session(session_id)
            raise SessionExpiredError(f"Session {session_id} has expired")
            
        return session

    def add_message(self, session_id: str, content: str, role: str) -> Message:
        """Añade un mensaje a una sesión"""
        session = self.get_session(session_id)
        message = Message(
            id=uuid4(),
            session_id=UUID(session.id),
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        session.messages.append(message)
        session.last_updated = datetime.utcnow()
        return message

    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Message]:
        """Obtiene los mensajes más recientes de una sesión"""
        session = self.get_session(session_id)
        return session.messages[-limit:]

    def close_session(self, session_id: str) -> None:
        """Cierra una sesión"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def _is_session_expired(self, session: ChatSession) -> bool:
        """Verifica si una sesión ha expirado"""
        expiration_time = session.last_updated + timedelta(seconds=self.session_timeout)
        return datetime.utcnow() > expiration_time