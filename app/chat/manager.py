from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
import logging
from datetime import datetime
import json

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
    ) -> str:
        """Crea una nueva sesión de chat y retorna su ID"""
        try:
            session = self.session_manager.create_session(
                user_id=user_id,
                board_id=board_id,
                metadata=metadata
            )
            logger.info(f"Nueva sesión de chat creada con ID: {session.id}")
            return str(session.id)  # Convertir UUID a string
        except Exception as e:
            logger.error(f"Error creando sesión de chat: {str(e)}")
            raise

    async def get_or_create_session(
        self,
        session_id: str,
        user_id: str,
        board_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Obtiene una sesión existente o crea una nueva"""
        try:
            # Intentar obtener la sesión
            try:
                # Convertir string a UUID si es necesario
                session_uuid = UUID(session_id) if isinstance(session_id, str) else session_id
                session = self.session_manager.get_session(session_uuid)
                return session
            except Exception:
                # Si no existe o hay error, crear nueva
                return self.session_manager.create_session(
                    user_id=user_id,
                    board_id=board_id,
                    metadata=metadata
                )
        except Exception as e:
            logger.error(f"Error en get_or_create_session: {str(e)}")
            # En caso de error, siempre crear una nueva
            return self.session_manager.create_session(
                user_id=user_id,
                board_id=board_id,
                metadata=metadata
            )

    async def process_message(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Procesa un mensaje del usuario y retorna la respuesta"""
        try:
            # Convertir string a UUID si es necesario
            session_uuid = UUID(session_id) if isinstance(session_id, str) else session_id
            
            # Obtener sesión y crear mensaje del usuario
            session = self.session_manager.get_session(session_uuid)
            
            user_message = Message(
                id=uuid4(),
                session_id=session_uuid,
                role="user",
                content=content,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            
            # Registrar mensaje del usuario
            self.session_manager.add_message(session_uuid, user_message)

            # Construir contexto para el orquestador
            context = self._build_conversation_context(session_uuid)
            
            # Serializar el contexto en un string para metadata
            context_str = json.dumps({
                "session_id": str(session_uuid),
                "board_id": session.board_id or "",
                "context": context
            })

            request_metadata = {"context": context_str}
            if metadata and "category" in metadata:
                request_metadata["category"] = metadata["category"]
            else:
                request_metadata["category"] = "general"

            # Procesar mediante el orquestrador
            llm_response = await self.orchestrator.process_query(
                query=content,
                response_type=ResponseType.CHAT,
                metadata=request_metadata
            )

            # Crear y registrar mensaje del asistente
            assistant_message = Message(
                id=uuid4(),
                session_id=session_uuid,
                role="assistant",
                content=llm_response.content,
                timestamp=datetime.utcnow(),
                metadata=llm_response.metadata
            )
            
            self.session_manager.add_message(session_uuid, assistant_message)

            # Construir y retornar respuesta
            return ChatResponse(
                message=assistant_message,
                context_used=context,
                metadata=llm_response.metadata
            )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Crear un mensaje de error para responder al usuario
            error_message = Message(
                id=uuid4(),
                session_id=UUID(session_id) if isinstance(session_id, str) else session_id,
                role="assistant",
                content="Lo siento, estoy teniendo problemas para procesar tu mensaje. ¿Podrías intentarlo de nuevo?",
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
            
            return ChatResponse(
                message=error_message,
                context_used={},
                metadata={"error": str(e)}
            )

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
                    "board_id": session.board_id
                }

            return context

        except Exception as e:
            logger.error(f"Error building context: {str(e)}")
            # Retornar contexto mínimo en caso de error
            return {
                "conversation_history": [],
                "session_metadata": {},
                "board_context": {}
            }

    async def close_chat_session(self, session_id: str) -> None:
        """Cierra una sesión de chat"""
        try:
            # Convertir string a UUID si es necesario
            session_uuid = UUID(session_id) if isinstance(session_id, str) else session_id
            self.session_manager.close_session(session_uuid)
            logger.info(f"Sesión de chat {session_id} cerrada")
        except Exception as e:
            logger.error(f"Error cerrando sesión de chat: {str(e)}")
            raise

    async def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Obtiene el historial de mensajes de una sesión"""
        try:
            # Convertir string a UUID si es necesario
            session_uuid = UUID(session_id) if isinstance(session_id, str) else session_id
            session = self.session_manager.get_session(session_uuid)
            messages = session.messages
            if limit:
                messages = messages[-limit:]
            return messages
        except Exception as e:
            logger.error(f"Error obteniendo historial de sesión: {str(e)}")
            return []
            
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene todas las sesiones de un usuario"""
        try:
            # Implementación basic - mejorar según se necesite
            sessions = []
            for session_id, session in self.session_manager.sessions.items():
                if session.user_id == user_id:
                    # Obtener último mensaje si existe
                    last_message = None
                    if session.messages:
                        last_message = session.messages[-1].content
                        
                    sessions.append({
                        "id": str(session_id),
                        "created_at": session.created_at.isoformat(),
                        "last_updated": session.last_updated.isoformat(),
                        "last_message": last_message,
                        "message_count": len(session.messages)
                    })
            return sessions
        except Exception as e:
            logger.error(f"Error obteniendo sesiones de usuario: {str(e)}")
            return []