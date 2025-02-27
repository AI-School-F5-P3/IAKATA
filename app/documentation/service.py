# app/documentation/service.py

from typing import Dict, Optional, List, Any
from pathlib import Path
import logging
from datetime import datetime

# Importaciones internas del módulo documentation
from .types import Document, DocumentType, DocumentFormat, DocumentTemplate
from .template_manager import TemplateStyleManager, ReportStyle
from .format_handler import FormatHandler
from .generator import DocumentGenerator
from .storage import DocumentStorage
from app.config.settings import get_settings

# Importaciones del sistema RAG
from app.vectorstore.vector_store import VectorStore
from app.llm.types import ResponseType, LLMResponse
from app.orchestrator.orchestrator import RAGOrchestrator

logger = logging.getLogger(__name__)

class DocumentationService:
    """
    Servicio centralizado para gestión de documentación.
    Coordina los diferentes componentes del sistema de documentación.
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        rag_orchestrator: RAGOrchestrator,
        base_dir: Optional[Path] = None
    ):
        """
        Inicializa el servicio de documentación.
        
        Args:
            vector_store: Instancia de VectorStore para búsquedas
            rag_orchestrator: Orquestador RAG para generación de contenido
            base_dir: Directorio base para almacenamiento (opcional)
        """
        self.vector_store = vector_store
        self.orchestrator = rag_orchestrator
        settings = get_settings()
        self.base_dir = base_dir or settings.DOCS_DIR
        
        # Inicializar componentes
        self.template_manager = TemplateStyleManager()
        self.generator = DocumentGenerator(rag_orchestrator.llm)
        self.format_handler = FormatHandler()
        self.storage = DocumentStorage(self.base_dir)
        
        logger.info("DocumentationService inicializado")

    async def generate_project_report(
        self,
        project_data: Dict[str, Any],
        template_id: str = "project_report",
        style: str = "default",
        output_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte de proyecto completo.
        
        Args:
            project_data: Datos del proyecto
            template_id: ID de la plantilla a usar
            style: Estilo del reporte
            output_format: Formato de salida opcional
            
        Returns:
            Dict con información del documento generado
        """
        try:
            logger.info(f"Generando reporte para proyecto con template {template_id}")
            
            # 1. Obtener y validar template con estilo
            template = self.template_manager.create_document_template(
                template_id=template_id,
                style=ReportStyle(style)
            )
            if not template:
                raise ValueError(f"Template no encontrado: {template_id}")

            # 2. Enriquecer contexto con RAG
            enriched_context = await self._build_documentation_context(project_data)
            
            # 3. Generar documento base
            document = await self.generator.generate_document(
                template=template,
                context=enriched_context,
                format=DocumentFormat(output_format) if output_format else None
            )
            
            # 4. Formatear documento
            formatted_content = self.format_handler.format_document(
                document=document,
                output_format=document.format,
                style_config=template.metadata.get("style_config")
            )
            
            # 5. Almacenar documento
            file_path = self.storage.save_document(document)
            
            return {
                "document_id": document.id,
                "file_path": str(file_path),
                "format": document.format.value,
                "metadata": {
                    "template": template_id,
                    "style": style,
                    "generated_at": datetime.utcnow().isoformat(),
                    "sections": len(document.sections)
                }
            }

        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
            raise

    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de plantillas disponibles con sus estilos.
        
        Returns:
            Lista de templates con su configuración
        """
        try:
            return self.template_manager.get_available_templates()
        except Exception as e:
            logger.error(f"Error obteniendo templates: {str(e)}")
            raise

    async def preview_template(
        self,
        template_id: str,
        style: str = "default"
    ) -> Dict[str, Any]:
        """
        Genera una vista previa de template con estilo.
        
        Args:
            template_id: ID del template
            style: Nombre del estilo
            
        Returns:
            Dict con información de preview
        """
        try:
            template = self.template_manager.create_document_template(
                template_id=template_id,
                style=ReportStyle(style)
            )
            
            if not template:
                raise ValueError(f"Template no encontrado: {template_id}")
                
            return {
                "template": {
                    "id": template.id,
                    "name": template.name,
                    "type": template.type.value,
                    "sections": template.sections
                },
                "style": style,
                "style_config": template.metadata.get("style_config"),
                "format": template.format.value
            }
            
        except Exception as e:
            logger.error(f"Error generando preview: {str(e)}")
            raise

    async def _build_documentation_context(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Construye contexto enriquecido para documentación usando RAG.
        
        Args:
            project_data: Datos del proyecto
            
        Returns:
            Contexto enriquecido con información relevante
        """
        try:
            # Preparar query para búsqueda
            search_query = self._extract_search_terms(project_data)
            
            # Realizar búsqueda RAG
            response = await self.orchestrator.process_query(
                query=search_query,
                response_type=ResponseType.DOCUMENTATION,
                metadata={"category": "documentation"}
            )
            
            # Construir contexto enriquecido
            return {
                "project_data": project_data,
                "rag_content": response.content if response else None,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "source": "RAG System",
                    "confidence": response.confidence if response else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error construyendo contexto: {str(e)}")
            # Retornar contexto básico si falla el enriquecimiento
            return {"project_data": project_data}

    def _extract_search_terms(self, project_data: Dict[str, Any]) -> str:
        """
        Extrae términos de búsqueda relevantes del proyecto.
        
        Args:
            project_data: Datos del proyecto
            
        Returns:
            Query para búsqueda
        """
        search_terms = []
        
        # Extraer campos relevantes
        if 'title' in project_data:
            search_terms.append(project_data['title'])
        if 'description' in project_data:
            search_terms.append(project_data['description'])
        if 'challenge' in project_data:
            if isinstance(project_data['challenge'], dict):
                search_terms.extend([
                    project_data['challenge'].get('description', ''),
                    project_data['challenge'].get('current_state', ''),
                    project_data['challenge'].get('target_state', '')
                ])
            else:
                search_terms.append(str(project_data['challenge']))
                
        return " ".join(filter(None, search_terms))
    async def convert_document_format(
        self,
        document_id: str,
        target_format: str,
        style: str = "default"
    ) -> Dict[str, Any]:
        """
        Convierte un documento existente a otro formato.
        
        Args:
            document_id: ID del documento a convertir
            target_format: Formato destino ("markdown", "html", "pdf", "json")
            style: Estilo a aplicar en la conversión
            
        Returns:
            Dict con información del documento convertido
        """
        try:
            # 1. Recuperar documento original
            document = await self.storage.get_document(document_id)
            if not document:
                raise ValueError(f"Documento no encontrado: {document_id}")
                
            # 2. Cambiar formato
            original_format = document.format
            document.format = DocumentFormat(target_format)
            
            # 3. Aplicar estilo si es necesario
            style_config = None
            if style != "default":
                style_config = self.template_manager.get_style_config(ReportStyle(style))
            
            # 4. Formatear contenido
            formatted_content = self.format_handler.format_document(
                document=document,
                output_format=document.format,
                style_config=style_config
            )
            
            # 5. Guardar documento en nuevo formato
            new_doc_id = await self.storage.save_document(document)
            
            return {
                "original_id": document_id,
                "original_format": original_format.value,
                "new_id": new_doc_id,
                "new_format": target_format,
                "converted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error convirtiendo formato: {str(e)}")
            raise