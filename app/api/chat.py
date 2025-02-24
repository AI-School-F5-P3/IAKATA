import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict
from core.chat.manager import ChatManager
from core.chat.types import ChatMessage
from core.chat.exceptions import ChatException
from core.chat.session import SessionManager
from core.setup import AIComponents, get_ai_components
from config import CustomLogger
from core.auth import HeaderValidator

router = APIRouter(prefix="/chat", tags=["chat"])
logger = CustomLogger("app.api.chat")


@router.post("/message")
async def process_chat(
    request: ChatRequest,
    authorization: str = Header(None),
    validator: HeaderValidator = Depends(),
    chat_manager: ChatManager = Depends(get_chat_manager),
    session_manager: SessionManager = Depends(get_session_manager)
):
    try:
        # Validar el token de autorización
        validator.validate_auth_header(authorization)
        user_id = "default_user"
        # Crear una nueva sesión si no existe
        #session_id = request.session_id or str(uuid.uuid4())
        #session = await session_manager.get_or_create_session(session_id)
        session = await session_manager.get_or_create_session(
            session_id=request.session_id,
            user_id=user_id
        )
        # Asegurar que el contexto sea un diccionario
        #context = request.context if isinstance(request.context, dict) else {}
        
        message = ChatMessage(
            content=request.message,
            context=request.context or {}
        )
        
        # Procesar mensaje
        response = await chat_manager.process_message(
            message=message,
            session=session
        )
        
        return {
            "status": "success",
            "message": request.message,
            "response": response.content if hasattr(response, 'content') else str(response),
            "session_id": session.id
        }
        
    except ChatException as ce:
        logger.error(f"ChatException: {str(ce)}")
        raise HTTPException(status_code=400, detail=str(ce))
    except Exception as e:
        logger.error(f"Error en chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    try:
        session = await session_manager.get_session(session_id)
        return {
            "status": "success",
            "session": session.to_dict()
        }
    except Exception as e:
        logger.error(f"Session not found: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Session not found: {str(e)}")