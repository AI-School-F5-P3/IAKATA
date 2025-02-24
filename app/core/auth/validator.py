from fastapi import HTTPException
from typing import Optional

class HeaderValidator:
    @staticmethod
    def validate_auth_header(authorization: Optional[str]) -> bool:
        """
        Solo valida que el header de autorización esté presente
        No valida el token ya que eso lo hace Node.js
        """
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail="Missing authorization header"
            )
        return True