# core/dependencies.py
from typing import Dict, Any
from fastapi import Depends, Header
from .setup import get_ai_components
from .orchestrator.orchestrator import RAGOrchestrator
from .chat.manager import ChatManager
from core.auth import HeaderValidator

# Obtener instancia singleton de AIComponents
ai_components = get_ai_components()

async def validate_auth(
    authorization: str = Header(None),
    validator: HeaderValidator = Depends()
) -> str:
    validator.validate_auth_header(authorization)
    return authorization

async def get_orchestrator() -> RAGOrchestrator:
    """
    Dependencia para obtener el orquestrador RAG
    """
    return ai_components.orchestrator

async def get_chat_manager() -> ChatManager:
    """
    Dependencia para obtener el chat manager
    """
    return ai_components.chat_manager

async def get_board_context(
    board_id: str = None,
    section_type: str = None,
    content: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Dependencia para construir el contexto del tablero
    """
    return {
        "board_id": board_id,
        "section_type": section_type,
        **(content or {})
    }