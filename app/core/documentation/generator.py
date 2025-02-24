# app/documentation/generator.py
import logging
from typing import Dict, List, Optional
from datetime import datetime
from typing import Any
from core.llm.types import LLMRequest, ResponseType, LLMResponse
from .types import Document, DocumentType, DocumentFormat, DocumentSection, DocumentTemplate

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """Clase principal para generación de documentos"""
    
    def __init__(self, llm_module):
        self.llm = llm_module
        
    async def generate_document(
        self,
        template: DocumentTemplate,
        context: Dict[str, Any],
        format: Optional[DocumentFormat] = None
    ) -> Document:
        """
        Genera un documento basado en un template y contexto
        Args:
            template: Template a utilizar
            context: Contexto del documento
            format: Formato de salida opcional
        Returns:
            Document generado
        """
        try:
            # Usar formato del template si no se especifica otro
            doc_format = format or template.format
            
            # Generar cada sección usando el LLM
            sections = []
            for section_name in template.sections:
                section_content = await self._generate_section(
                    section_name,
                    template.type,
                    context
                )
                
                if section_content:
                    sections.append(DocumentSection(
                        title=section_name,
                        content=section_content,
                        order=len(sections)
                    ))
            
            # Crear documento
            document = Document(
                id=f"{template.id}_{datetime.utcnow().timestamp()}",
                type=template.type,
                title=template.name,
                sections=sections,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                format=doc_format,
                metadata={
                    "template_id": template.id,
                    "context": context
                }
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Error generando documento: {str(e)}")
            raise
            
    # En app/documentation/generator.py
    async def _generate_section(
        self,
        section_name: str,
        doc_type: DocumentType,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Genera el contenido de una sección específica
        """
        try:
            # Crear LLMRequest con formato correcto
            request = LLMRequest(
                query=f"Genera el contenido para la sección '{section_name}' del documento tipo {doc_type.value}.",
                response_type=ResponseType.DOCUMENTATION,
                context=context
            )
            
            # Obtener respuesta del LLM
            response = await self.llm.process_request(request)
            
            return response.content if response else None
            
        except Exception as e:
            logger.error(f"Error generando sección {section_name}: {str(e)}")
            return None