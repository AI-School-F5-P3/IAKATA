# app/documentation/types.py
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class DocumentType(Enum):
    """Tipos de documentos que se pueden generar"""
    REPORT = "report"
    SUMMARY = "summary"
    ANALYSIS = "analysis"
    LEARNING = "learning"

class DocumentFormat(Enum):
    """Formatos de salida disponibles"""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"

class DocumentSection(BaseModel):
    """Sección de un documento"""
    title: str
    content: str
    order: int
    metadata: Optional[Dict[str, Any]] = None

class Document(BaseModel):
    """Modelo base para documentos"""
    id: str
    type: DocumentType
    title: str
    sections: List[DocumentSection]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    format: DocumentFormat = DocumentFormat.MARKDOWN

class DocumentTemplate(BaseModel):
    """Template para generación de documentos"""
    id: str
    name: str
    type: DocumentType
    sections: List[str]
    format: DocumentFormat
    metadata: Optional[Dict[str, Any]] = None