from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Union

class FormData(BaseModel):
    idForm: str = Field(..., description="Id de la sección.")
    description: str = Field(..., description="Descripción de la sección")

class ResponseOutput(BaseModel):
    status: str
    message: str
    data: dict

class Context(BaseModel):
    pass

class ChatMessage(BaseModel):
    content: Optional[str] = None
    query: Optional[str] = None  # Para compatibilidad con el frontend
    context: Optional[Dict[str, Any]] = None  # Para compatibilidad con el frontend
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    board_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    # Método para manejar compatibilidad entre formatos
    def get_content(self) -> str:
        """Obtiene el contenido del mensaje, ya sea de content o query"""
        return self.content or self.query or ""
    
    def get_metadata(self) -> Dict[str, Any]:
        """Combina metadata y context para compatibilidad"""
        combined = self.metadata or {}
        if self.context:
            combined.update({"context": self.context})
        return combined

class ChatResponse(BaseModel):
    message: Union[str, Dict[str, Any]]  # Permite string o un objeto Message
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
    insights: Optional[List[Dict[str, Any]]] = None
    status: str = "success"
    
    # Método para convertir a formato compatible con frontend
    def dict(self, *args, **kwargs):
        """Sobrescribe el método dict para asegurar compatibilidad"""
        data = super().dict(*args, **kwargs)
        
        # Si message es un objeto con content, extraer el content
        if isinstance(data["message"], dict) and "content" in data["message"]:
            data["message"] = data["message"]["content"]
            
        return data