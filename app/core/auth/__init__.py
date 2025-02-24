from fastapi import HTTPException
from typing import Optional

class HeaderValidator:
    """
    Validador de headers para FastAPI que solo verifica la presencia
    del token sin validar su contenido (la validación la hace Node.js)
    """
    @staticmethod
    def validate_auth_header(authorization: Optional[str] = None) -> bool:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "error": "No authorization header provided",
                    "code": "NO_TOKEN"
                }
            )
        return True

    @staticmethod
    def get_token_from_header(authorization: str) -> str:
        """Extrae el token del header de autorización"""
        return authorization.split(' ')[1] if authorization else None

    @staticmethod
    def extract_user_id(headers: dict) -> Optional[str]:
        """Extrae el user_id de los headers"""
        return headers.get('X-User-ID')

# Exportar solo lo necesario
__all__ = ['HeaderValidator']