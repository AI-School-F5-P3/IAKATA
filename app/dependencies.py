from core.setup import AIComponents
from fastapi import Depends, Header
from core.auth import HeaderValidator

settings = get_settings()


async def get_auth_header(authorization: str = Header(None)) -> str:
    validator = HeaderValidator()
    validator.validate_auth_header(authorization)
    return authorization




async def get_ai_components():
    """Dependencia para obtener componentes de IA"""
    return AIComponents()