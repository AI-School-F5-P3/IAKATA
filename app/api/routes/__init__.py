from fastapi import APIRouter, Depends, HTTPException, Header
from core.orchestrator.orchestrator import RAGOrchestrator
from core.chat.manager import ChatManager
from typing import Dict, Any, Optional
from pydantic import BaseModel
from core.setup import get_ai_components
from core.dependencies import get_orchestrator, get_chat_manager, get_board_context
from core.auth import HeaderValidator

class BoardRequest(BaseModel):
    boardId: str
    sectionType: str
    content: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

ai_components = get_ai_components()

# Inicializar routers
api_router = APIRouter()
rag_router = APIRouter(prefix="/rag", tags=["rag"])
chat_router = APIRouter(prefix="/chat", tags=["chat"])
board_router = APIRouter(prefix="/board", tags=["board"])

async def validate_token(
    authorization: str = Header(None),
    validator: HeaderValidator = Depends()
) -> bool:
    return validator.validate_auth_header(authorization)

# Configurar rutas RAG
@rag_router.post("/analyze")
async def analyze_board(
    data: BoardRequest,
    authorized: bool = Depends(validate_token),
    orchestrator: RAGOrchestrator = Depends(get_orchestrator)
):
    try:
        response = await orchestrator.process_board_request(
            board_id=data.boardId,
            section_type=data.sectionType,
            content=data.content,
            context=data.context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Configurar rutas de chat
@chat_router.post("/message")
async def process_message(
    message: Dict[str, str],
    authorized: bool = Depends(validate_token),
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    try:
        response = await chat_manager.process_message(
            session_id=message.get("sessionId"),
            content=message.get("content"),
            metadata=message.get("metadata")
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Incluir todos los routers en el router principal
api_router.include_router(rag_router)
api_router.include_router(chat_router)
api_router.include_router(board_router)

# Exportar el router principal
__all__ = ['api_router']