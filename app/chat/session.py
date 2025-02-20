from typing import Dict, Optional, List
from uuid import UUID, uuid4
import logging
from datetime import datetime, timedelta

from .types import ChatSession, Message
from .exceptions import SessionNotFoundError, SessionExpiredError

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, session_timeout: int = 3600):  # timeout en segundos
        self.sessions: Dict[UUID, ChatSession] = {}
        self.session_timeout = session_timeout

    def create_session(
        self,
        user_id: str,
        board_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> ChatSession:
        """Crea una nueva sesión de chat"""
        session = ChatSession(
            id=uuid4(),  # Cambiado aquí
            user_id=user_id,
            board_id=board_id,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            metadata=metadata or {}
        )
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: UUID) -> ChatSession:
        """Obtiene una sesión existente"""
        session = self.sessions.get(session_id)
        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        if self._is_session_expired(session):
            self.close_session(session_id)
            raise SessionExpiredError(f"Session {session_id} has expired")
            
        return session

    def add_message(self, session_id: UUID, message: Message) -> None:
        """Añade un mensaje a una sesión"""
        session = self.get_session(session_id)
        session.messages.append(message)
        session.last_updated = datetime.utcnow()

    def get_recent_messages(
        self,
        session_id: UUID,
        limit: int = 10
    ) -> List[Message]:
        """Obtiene los mensajes más recientes de una sesión"""
        session = self.get_session(session_id)
        return session.messages[-limit:]

    def close_session(self, session_id: UUID) -> None:
        """Cierra una sesión"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def _is_session_expired(self, session: ChatSession) -> bool:
        """Verifica si una sesión ha expirado"""
        expiration_time = session.last_updated + timedelta(seconds=self.session_timeout)
        return datetime.utcnow() > expiration_time