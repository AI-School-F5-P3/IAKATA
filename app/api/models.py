from pydantic import BaseModel, Field
from typing import Optional

class FormData(BaseModel):
    id: str = Field(..., description="Id de la sección.")
    userId: int = Field(..., description="Id del usuario.")
    description: str = Field(..., description="Descripción de la sección")
    name: Optional[str] = Field(None, description="Nombre (opcional)")

class ResponseOutput(BaseModel):
    status: str
    message: str
    data: dict

class Context(BaseModel):
    pass