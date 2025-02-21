# app/documentation/storage.py
from typing import Dict, List, Optional
import json
from pathlib import Path
import logging
from .types import Document, DocumentFormat
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentStorage:
    """Gestiona el almacenamiento de documentos generados"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def save_document(self, document: Document) -> Path:
        """
        Guarda un documento en el sistema de archivos
        Args:
            document: Documento a guardar
        Returns:
            Path al documento guardado
        """
        try:
            # Crear directorio para el tipo de documento
            doc_dir = self.base_dir / document.type.value
            doc_dir.mkdir(exist_ok=True)
            
            # Determinar extensión basada en formato
            extension = self._get_extension(document.format)
            
            # Generar nombre de archivo
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{document.id}_{timestamp}{extension}"
            file_path = doc_dir / filename
            
            # Guardar contenido
            content = self._format_document(document)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return file_path
            
        except Exception as e:
            logger.error(f"Error guardando documento: {str(e)}")
            raise
            
    def _get_extension(self, format: DocumentFormat) -> str:
        """Obtiene la extensión de archivo apropiada"""
        extensions = {
            DocumentFormat.MARKDOWN: ".md",
            DocumentFormat.HTML: ".html",
            DocumentFormat.JSON: ".json",
            DocumentFormat.PDF: ".pdf"
        }
        return extensions.get(format, ".txt")
        
    def _format_document(self, document: Document) -> str:
        """Formatea el documento según su tipo"""
        if document.format == DocumentFormat.MARKDOWN:
            return self._format_markdown(document)
        elif document.format == DocumentFormat.HTML:
            return self._format_html(document)
        elif document.format == DocumentFormat.JSON:
            return self._format_json(document)
        else:
            raise ValueError(f"Formato no soportado: {document.format}")
            
    def _format_markdown(self, document: Document) -> str:
        """Formatea documento en Markdown"""
        content = [f"# {document.title}\n"]
        
        for section in sorted(document.sections, key=lambda s: s.order):
            content.extend([
                f"\n## {section.title}\n",
                section.content,
                "\n"
            ])
            
        return "\n".join(content)
        
    def _format_html(self, document: Document) -> str:
        """Formatea documento en HTML"""
        sections_html = []
        for section in sorted(document.sections, key=lambda s: s.order):
            sections_html.append(
                f"<section><h2>{section.title}</h2>{section.content}</section>"
            )
            
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>{document.title}</title></head>
        <body>
            <h1>{document.title}</h1>
            {''.join(sections_html)}
        </body>
        </html>
        """
        
    def _format_json(self, document: Document) -> str:
        """Formatea documento en JSON"""
        return json.dumps({
            "id": document.id,
            "type": document.type.value,
            "title": document.title,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "order": section.order
                }
                for section in sorted(document.sections, key=lambda s: s.order)
            ],
            "metadata": document.metadata
        }, indent=2)