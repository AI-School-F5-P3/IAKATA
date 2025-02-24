# app/documentation/templates.py
from typing import Dict, List, Optional
import logging
from .types import DocumentTemplate, DocumentType, DocumentFormat

logger = logging.getLogger(__name__)

class TemplateManager:
    """Gestiona templates para generación de documentos"""
    
    def __init__(self):
        self.templates: Dict[str, DocumentTemplate] = {}
        self._load_default_templates()
        
    def _load_default_templates(self):
        """Carga templates predefinidos"""
        # Template para reportes de proyecto
        self.templates["project_report"] = DocumentTemplate(
            id="project_report",
            name="Reporte de Proyecto",
            type=DocumentType.REPORT,
            format=DocumentFormat.MARKDOWN,
            sections=[
                "Resumen Ejecutivo",
                "Proceso de Mejora",
                "Resultados y Métricas",
                "Lecciones Aprendidas",
                "Anexos"
            ]
        )
        
        # Template para resúmenes de aprendizaje
        self.templates["learning_summary"] = DocumentTemplate(
            id="learning_summary",
            name="Resumen de Aprendizaje",
            type=DocumentType.LEARNING,
            format=DocumentFormat.MARKDOWN,
            sections=[
                "Conceptos Clave",
                "Insights Principales",
                "Aplicaciones Prácticas",
                "Recomendaciones"
            ]
        )
    
    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        """Obtiene un template por su ID"""
        return self.templates.get(template_id)
    
    def add_template(self, template: DocumentTemplate) -> None:
        """Añade un nuevo template"""
        self.templates[template.id] = template
    
    def list_templates(self) -> List[DocumentTemplate]:
        """Lista todos los templates disponibles"""
        return list(self.templates.values())