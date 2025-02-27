from fastapi import APIRouter, HTTPException, Depends
from app.api.models import ChatMessage, ChatResponse
from app.api.services.chat_services import process_chat_message
import logging
from typing import Dict, Any, Optional
from uuid import uuid4

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/message", response_model=ChatResponse)
async def chat_endpoint(data: dict):
    """
    Endpoint para procesar mensajes del chatbot
    
    El frontend envía un objeto con:
    - query: El mensaje del usuario
    - context: Información contextual (userId, userName, tableId, sessionId)
    """
    try:
        # Extraer datos del request
        content = data.get("query", "")
        context = data.get("context", {})
        
        # Extraer información del contexto
        user_id = context.get("userId") or str(uuid4())
        session_id = context.get("sessionId")
        board_id = context.get("tableId")
        
        # Preparar metadata adicional
        metadata = {
            "userName": context.get("userName"),
            "source": "chat_widget",
            "category": "general"
        }
        
        # Procesar el mensaje
        response = await process_chat_message(
            content=content,
            user_id=user_id,
            session_id=session_id,
            board_id=board_id,
            metadata=metadata
        )
        
        # Asegurar que la respuesta incluye el campo 'message'
        if 'message' not in response:
            # Si la respuesta original no tiene message pero tiene content
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                response = {
                    "message": response.message.content,
                    "session_id": response.get("session_id", session_id),
                    "status": "success"
                }
        
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """
    Obtiene las sesiones de chat de un usuario
    """
    from app.chat.manager import ChatManager
    from app.api.services.chat_services import chat_manager
    
    try:
        if not chat_manager:
            return {"sessions": []}
            
        sessions = await chat_manager.get_user_sessions(user_id)
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error getting user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")