from pydantic import BaseModel, Field
from typing import Optional

class FormData(BaseModel):
    idForm: str = Field(..., description="Id de la sección.")
    description: str = Field(..., description="Descripción de la sección")

class ResponseOutput(BaseModel):
    status: str
    message: str
    data: dict

class Context(BaseModel):
    pass