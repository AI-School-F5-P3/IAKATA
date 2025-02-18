from typing import Dict, List, Optional, Any
from uuid import UUID
import logging
from datetime import datetime

from app.orchestrator.orchestrator import RAGOrchestrator
from app.llm.types import ResponseType, LLMResponse
from .session import SessionManager
from .types import Message, ChatResponse
from .exceptions import MessageProcessingError, ContextBuildError

logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(
        self,
        orchestrator: RAGOrchestrator,
        context_window_size: int = 10,
        session_timeout: int = 3600
    ):
        self.orchestrator = orchestrator
        self.session_manager = SessionManager(session_timeout=session_timeout)
        self.context_window_size = context_window_size

    async def create_chat_session(
        self,
        user_id: str,
        board_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Crea una nueva sesión de chat y retorna su ID"""
        session = self.session_manager.create_session(
            user_id=user_id,
            board_id=board_id,
            metadata=metadata
        )
        return session.id

    async def process_message(
        self,
        session_id: UUID,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Procesa un mensaje del usuario y retorna la respuesta"""
        try:
            # Obtener sesión y crear mensaje del usuario
            session = self.session_manager.get_session(session_id)
            
            user_message = Message(
                id=UUID.uuid4(),
                session_id=session_id,
                role="user",
                content=content,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            
            # Registrar mensaje del usuario
            self.session_manager.add_message(session_id, user_message)

            # Construir contexto para el orquestador
            context = self._build_conversation_context(session_id)
            
            # Procesar mediante el orquestador
            llm_response = await self.orchestrator.process_query(
                query=content,
                response_type=ResponseType.CHAT,
                metadata={
                    "session_id": str(session_id),
                    "board_id": session.board_id or "",
                    "context": context
                }
            )

            # Crear y registrar mensaje del asistente
            assistant_message = Message(
                id=UUID.uuid4(),
                session_id=session_id,
                role="assistant",
                content=llm_response.content,
                timestamp=datetime.utcnow(),
                metadata=llm_response.metadata
            )
            
            self.session_manager.add_message(session_id, assistant_message)

            # Construir y retornar respuesta
            return ChatResponse(
                message=assistant_message,
                context_used=context,
                metadata=llm_response.metadata
            )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise MessageProcessingError(f"Failed to process message: {str(e)}")

    def _build_conversation_context(self, session_id: UUID) -> Dict[str, Any]:
        """Construye el contexto de la conversación para el orquestador"""
        try:
            # Obtener sesión y mensajes recientes
            session = self.session_manager.get_session(session_id)
            recent_messages = self.session_manager.get_recent_messages(
                session_id,
                self.context_window_size
            )

            # Construir contexto
            context = {
                "conversation_history": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in recent_messages
                ],
                "session_metadata": session.metadata or {},
                "board_context": {}
            }

            # Añadir contexto del tablero si existe
            if session.board_id:
                context["board_context"] = {
                    "board_id": session.board_id,
                    # Aquí se podría añadir más información específica del tablero
                }

            return context

        except Exception as e:
            logger.error(f"Error building context: {str(e)}")
            raise ContextBuildError(f"Failed to build conversation context: {str(e)}")

    async def close_chat_session(self, session_id: UUID) -> None:
        """Cierra una sesión de chat"""
        self.session_manager.close_session(session_id)

    async def get_session_history(
        self,
        session_id: UUID,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Obtiene el historial de mensajes de una sesión"""
        session = self.session_manager.get_session(session_id)
        messages = session.messages
        if limit:
            messages = messages[-limit:]
        return messages