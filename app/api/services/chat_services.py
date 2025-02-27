from app.chat.manager import ChatManager
from app.orchestrator.orchestrator import RAGOrchestrator
from app.llm.types import ResponseType
from app.vectorstore.vector_store import VectorStore
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
import logging
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
import json

logger = logging.getLogger(__name__)

# Singleton para asegurar una sola instancia de los componentes
_components = None

def get_components():
    global _components
    if _components is None:
        try:
            vector_store = VectorStore()
            try:
                from pathlib import Path
                vector_store_path = Path("app/vectorstore/processed/vectors")
                if vector_store_path.exists():
                    vector_store.load(vector_store_path)
                    logger.info("Vector store loaded successfully")
                else:
                    logger.warning("Vector store directory not found, using empty store")
            except Exception as ve:
                logger.error(f"Error loading vector store: {str(ve)}")
            
            llm = LLMModule()
            validator = ResponseValidator()
            orchestrator = RAGOrchestrator(vector_store=vector_store, llm=llm, validator=validator)
            chat_manager = ChatManager(orchestrator=orchestrator)
            
            _components = {
                "vector_store": vector_store,
                "llm": llm,
                "validator": validator,
                "orchestrator": orchestrator,
                "chat_manager": chat_manager
            }
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}")
            raise
    
    return _components

def get_chat_manager():
    return get_components()["chat_manager"]

async def process_chat_message(content: str, user_id: str, 
                             session_id: Optional[str] = None,
                             board_id: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None):
    """
    Procesa un mensaje del chat con gestión mejorada de sesiones
    """
    try:
        chat_manager = get_chat_manager()
        
        # Generar nuevo session_id si es necesario
        if not session_id:
            session_id = str(uuid4())

        # Validar y convertir session_id
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            logger.warning(f"Invalid UUID format: {session_id}, generating new")
            session_id = str(uuid4())
            session_uuid = UUID(session_id)

        # Gestión de sesión con doble verificación
        try:
            session = chat_manager.session_manager.get_session(session_uuid)
            if session.user_id != user_id:
                raise ValueError("User ID mismatch for session")
        except Exception as session_error:
            logger.info(f"Creating new session: {str(session_error)}")
            session_id = await chat_manager.create_chat_session(
                user_id=user_id,
                board_id=board_id,
                metadata=metadata or {}
            )
            session_uuid = UUID(session_id)

        # Procesamiento con timeout integrado
        response = await chat_manager.process_message(
            session_id=session_uuid,
            content=content,
            metadata=metadata or {}
        )

        # Formatear respuesta con estructura extendida
        return {
            "message": response.message.content,
            "session_id": str(session_id),
            "metadata": response.metadata,
            "insights": extract_insights(response),
            "context_summary": {
                "current_step": response.context_used.get("current_phase", "analysis"),
                "related_challenges": response.context_used.get("related_challenges", [])[:3]
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        return {
            "message": "Estoy teniendo dificultades técnicas. Por favor intenta nuevamente.",
            "session_id": session_id or str(uuid4()),
            "status": "error",
            "error_code": "PROCESSING_ERROR"
        }

def extract_insights(response):
    """Genera insights con formato mejorado"""
    insights = []
    try:
        if hasattr(response, 'context_used'):
            for item in response.context_used.get('relevant_texts', [])[:3]:
                insights.append({
                    "text": (item['text'][:200] + '...') if len(item['text']) > 200 else item['text'],
                    "relevance": round(item.get('score', 0) * 100),
                    "source": item.get('source', 'unknown')
                })
        return insights
    except Exception as e:
        logger.error(f"Error extracting insights: {str(e)}")
        return []