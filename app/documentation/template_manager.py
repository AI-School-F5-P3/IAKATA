from typing import Dict, List, Optional
from pydantic import BaseModel
from enum import Enum
from pathlib import Path
import jinja2
import logging
import json
from .types import DocumentTemplate, DocumentType, DocumentFormat

logger = logging.getLogger(__name__)

class ReportStyle(str, Enum):
    """Estilos disponibles para reportes"""
    DEFAULT = "default"
    MINIMAL = "minimal"
    DETAILED = "detailed"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"

class ReportFormat(str, Enum):
    """Formatos de salida disponibles"""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"

class TemplateConfig(BaseModel):
    """Configuración de una plantilla"""
    id: str
    name: str
    description: str
    type: DocumentType
    format: DocumentFormat
    sections: List[str]
    styles: List[ReportStyle]
    metadata: Optional[Dict] = None

class TemplateStyleManager:
    """
    Gestor de plantillas y estilos para reportes
    """
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path("app/documentation/templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        self.templates: Dict[str, TemplateConfig] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Carga las plantillas predeterminadas"""
        default_templates = {
            "project_summary": TemplateConfig(
                id="project_summary",
                name="Resumen de Proyecto",
                description="Resumen ejecutivo del proyecto Lean Kata",
                type=DocumentType.SUMMARY,
                format=DocumentFormat.MARKDOWN,
                sections=[
                    "Descripción General",
                    "Objetivos",
                    "Logros Principales",
                    "Próximos Pasos"
                ],
                styles=[
                    ReportStyle.DEFAULT,
                    ReportStyle.MINIMAL,
                    ReportStyle.EXECUTIVE
                ]
            ),
            "detailed_report": TemplateConfig(
                id="detailed_report",
                name="Reporte Detallado",
                description="Informe detallado con todos los elementos del proyecto",
                type=DocumentType.REPORT,
                format=DocumentFormat.MARKDOWN,
                sections=[
                    "Resumen Ejecutivo",
                    "Descripción del Challenge",
                    "Estado Actual y Objetivo",
                    "Experimentos Realizados",
                    "Resultados y Métricas",
                    "Aprendizajes",
                    "Recomendaciones",
                    "Anexos"
                ],
                styles=[
                    ReportStyle.DEFAULT,
                    ReportStyle.DETAILED,
                    ReportStyle.TECHNICAL
                ]
            ),
            "learning_report": TemplateConfig(
                id="learning_report",
                name="Reporte de Aprendizajes",
                description="Resumen de aprendizajes y mejores prácticas",
                type=DocumentType.LEARNING,
                format=DocumentFormat.MARKDOWN,
                sections=[
                    "Insights Principales",
                    "Prácticas Efectivas",
                    "Desafíos y Soluciones",
                    "Recomendaciones"
                ],
                styles=[
                    ReportStyle.DEFAULT,
                    ReportStyle.MINIMAL,
                    ReportStyle.DETAILED
                ]
            ),
            "experiment_report": TemplateConfig(
                id="experiment_report",
                name="Reporte de Experimentos",
                description="Análisis detallado de experimentos realizados",
                type=DocumentType.ANALYSIS,
                format=DocumentFormat.MARKDOWN,
                sections=[
                    "Resumen de Experimentos",
                    "Hipótesis y Predicciones",
                    "Metodología",
                    "Resultados",
                    "Análisis",
                    "Conclusiones"
                ],
                styles=[
                    ReportStyle.DEFAULT,
                    ReportStyle.TECHNICAL,
                    ReportStyle.DETAILED
                ]
            )
        }

        self.templates.update(default_templates)
        logger.info(f"Cargadas {len(default_templates)} plantillas predeterminadas")

    def get_template_config(self, template_id: str) -> Optional[TemplateConfig]:
        """Obtiene la configuración de una plantilla"""
        return self.templates.get(template_id)

    def get_available_templates(self) -> List[Dict]:
        """Retorna lista de plantillas disponibles"""
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "type": template.type.value,
                "format": template.format.value,
                "styles": [style.value for style in template.styles]
            }
            for template in self.templates.values()
        ]

    def get_style_config(self, style: ReportStyle) -> Dict:
        """Obtiene la configuración para un estilo específico"""
        style_configs = {
            ReportStyle.DEFAULT: {
                "css_framework": "tailwind",
                "font_size": "text-base",
                "headings": {
                    "h1": "text-4xl font-bold mb-8",
                    "h2": "text-2xl font-semibold mb-4",
                    "h3": "text-xl font-medium mb-3"
                },
                "sections": "mb-8",
                "paragraphs": "mb-4"
            },
            ReportStyle.MINIMAL: {
                "css_framework": "tailwind",
                "font_size": "text-sm",
                "headings": {
                    "h1": "text-3xl font-bold mb-6",
                    "h2": "text-xl font-semibold mb-3",
                    "h3": "text-lg font-medium mb-2"
                },
                "sections": "mb-6",
                "paragraphs": "mb-3"
            },
            ReportStyle.DETAILED: {
                "css_framework": "tailwind",
                "font_size": "text-base",
                "headings": {
                    "h1": "text-5xl font-bold mb-10",
                    "h2": "text-3xl font-semibold mb-6",
                    "h3": "text-2xl font-medium mb-4"
                },
                "sections": "mb-12",
                "paragraphs": "mb-6"
            },
            ReportStyle.EXECUTIVE: {
                "css_framework": "tailwind",
                "font_size": "text-lg",
                "headings": {
                    "h1": "text-4xl font-bold mb-8 text-blue-600",
                    "h2": "text-2xl font-semibold mb-4 text-blue-500",
                    "h3": "text-xl font-medium mb-3 text-blue-400"
                },
                "sections": "mb-10",
                "paragraphs": "mb-4"
            },
            ReportStyle.TECHNICAL: {
                "css_framework": "tailwind",
                "font_size": "text-base",
                "headings": {
                    "h1": "text-3xl font-mono font-bold mb-8",
                    "h2": "text-2xl font-mono font-semibold mb-6",
                    "h3": "text-xl font-mono font-medium mb-4"
                },
                "sections": "mb-8",
                "paragraphs": "mb-4 font-mono"
            }
        }
        return style_configs.get(style, style_configs[ReportStyle.DEFAULT])

    def create_document_template(
        self,
        template_id: str,
        style: ReportStyle = ReportStyle.DEFAULT
    ) -> Optional[DocumentTemplate]:
        """
        Crea una plantilla de documento con el estilo especificado
        """
        try:
            template_config = self.get_template_config(template_id)
            if not template_config:
                logger.error(f"Plantilla no encontrada: {template_id}")
                return None

            # Verificar que el estilo es válido para la plantilla
            if style not in template_config.styles:
                logger.warning(f"Estilo {style} no disponible para plantilla {template_id}")
                style = ReportStyle.DEFAULT

            # Crear DocumentTemplate
            document_template = DocumentTemplate(
                id=template_id,
                name=template_config.name,
                type=template_config.type,
                sections=template_config.sections,
                format=template_config.format,
                metadata={
                    "style": style.value,
                    "style_config": self.get_style_config(style),
                    "description": template_config.description,
                    **template_config.metadata or {}
                }
            )

            return document_template

        except Exception as e:
            logger.error(f"Error creando plantilla de documento: {str(e)}")
            return None

    def add_custom_template(self, template_config: TemplateConfig) -> bool:
        """Añade una plantilla personalizada"""
        try:
            if template_config.id in self.templates:
                logger.warning(f"Ya existe una plantilla con ID {template_config.id}")
                return False

            self.templates[template_config.id] = template_config
            return True

        except Exception as e:
            logger.error(f"Error añadiendo plantilla personalizada: {str(e)}")
            return False

    def save_templates(self) -> bool:
        """Guarda las plantillas en un archivo JSON"""
        try:
            templates_file = self.templates_dir / "templates.json"
            templates_data = {
                template_id: template.dict()
                for template_id, template in self.templates.items()
            }

            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.error(f"Error guardando plantillas: {str(e)}")
            return False

    def load_templates(self) -> bool:
        """Carga plantillas desde un archivo JSON"""
        try:
            templates_file = self.templates_dir / "templates.json"
            if not templates_file.exists():
                logger.info("No se encontró archivo de plantillas personalizadas")
                return False

            with open(templates_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)

            for template_id, template_data in templates_data.items():
                template_config = TemplateConfig(**template_data)
                self.templates[template_id] = template_config

            return True

        except Exception as e:
            logger.error(f"Error cargando plantillas: {str(e)}")
            return False