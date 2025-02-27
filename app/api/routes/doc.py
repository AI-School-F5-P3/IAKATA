# Modificación en app/api/routes/doc.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from app.orchestrator.orchestrator import RAGOrchestrator
from app.documentation.generator import DocumentGenerator
from app.documentation.template_manager import TemplateStyleManager
from app.documentation.storage import DocumentStorage
from app.documentation.types import DocumentFormat, Document
from app.documentation.analysis_integrator import AnalysisDocumentIntegrator

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependencia para obtener el integrador
async def get_doc_integrator():
    """Dependencia para obtener el integrador de documentación y análisis"""
    # Usar los componentes ya inicializados en el módulo de servicios
    from app.api.services.chat_services import get_components
    
    components = get_components()
    orchestrator = components["orchestrator"]
    
    # Inicializar componentes de documentación
    template_manager = TemplateManager()
    doc_generator = DocumentGenerator(orchestrator.llm)
    
    # Crear y devolver el integrador
    integrator = AnalysisDocumentIntegrator(
        document_generator=doc_generator,
        template_manager=template_manager,
        orchestrator=orchestrator,
        vector_store=components["vector_store"]
    )
    
    return integrator

# Mantener el endpoint original
@router.post("/generate-documentation")
async def generate_documentation(project_data: dict):
    try:
        # Asumiendo que tienes acceso al orchestrator configurado
        document = await orchestrator.generate_documentation(
            project_data=project_data,
            template_id="project_report"  # Este es el template por defecto
        )
        
        return {
            "status": "success",
            "message": "Documentación generada exitosamente",
            "data": {
                "doc_id": document.id,
                "title": document.title,
                "sections": len(document.sections),
                "format": document.format.value
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando documentación: {str(e)}"
        )

@router.post("/generate-documentation-with-analysis")
async def generate_documentation_with_analysis(
    project_data: dict,
    integrator: AnalysisDocumentIntegrator = Depends(get_doc_integrator)
):
    """
    Genera documentación que integra análisis del proyecto
    """
    try:
        # Obtener datos necesarios
        project_id = project_data.get("project_id")
        if not project_id:
            raise HTTPException(status_code=400, detail="Se requiere project_id")
            
        template_id = project_data.get("template_id", "project_report")
        format_str = project_data.get("format", "markdown")
        
        # Convertir formato
        try:
            format = DocumentFormat[format_str.upper()]
        except KeyError:
            format = DocumentFormat.MARKDOWN
        
        # Generar documento con análisis
        document = await integrator.generate_analysis_report(
            project_id=project_id,
            template_id=template_id,
            format=format,
            include_raw_metrics=project_data.get("include_raw_metrics", False)
        )
        
        # Guardar documento
        storage = DocumentStorage(Path("app/documentation/processed/docs"))
        file_path = storage.save_document(document)
        
        return {
            "status": "success",
            "message": "Documentación con análisis generada exitosamente",
            "data": {
                "doc_id": document.id,
                "title": document.title,
                "sections": len(document.sections),
                "format": document.format.value,
                "file_path": str(file_path)
            }
        }
    except Exception as e:
        logger.error(f"Error en generate_documentation_with_analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando documentación con análisis: {str(e)}"
        )

# Endpoint para listar templates disponibles
@router.get("/templates")
async def list_templates():
    """
    Lista los templates disponibles para generación de documentos
    
    Returns:
        Lista de templates disponibles
    """
    try:
        template_manager = TemplateManager()
        templates = template_manager.list_templates()
        
        return [
            {
                "id": template.id,
                "name": template.name,
                "type": template.type.value,
                "format": template.format.value,
                "sections": template.sections
            }
            for template in templates
        ]
    except Exception as e:
        logger.error(f"Error listando templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listando templates: {str(e)}"
        )

# Endpoint para obtener documentos generados para un proyecto
@router.get("/project/{project_id}")
async def get_project_documents(project_id: str):
    """
    Obtiene los documentos generados para un proyecto específico
    
    Args:
        project_id: ID del proyecto
        
    Returns:
        Lista de documentos generados
    """
    try:
        # Este enfoque depende de cómo almacenas documentos
        # Implementar lógica para buscar documentos por project_id en metadatos
        
        # Ejemplo simple: buscar en directorio por nombre de archivo
        docs_dir = Path("app/documentation/processed/docs")
        
        documents = []
        # Buscar en todos los subdirectorios por tipo de documento
        for doc_type_dir in docs_dir.iterdir():
            if doc_type_dir.is_dir():
                for doc_file in doc_type_dir.glob(f"*{project_id}*"):
                    documents.append({
                        "id": doc_file.stem,
                        "path": str(doc_file),
                        "type": doc_type_dir.name,
                        "created_at": doc_file.stat().st_mtime,
                        "format": doc_file.suffix[1:],  # Eliminar el punto
                        "file_name": doc_file.name
                    })
        
        return {
            "status": "success",
            "project_id": project_id,
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error obteniendo documentos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo documentos: {str(e)}"
        )

# Endpoint para obtener un documento específico
@router.get("/view/{doc_id}")
async def view_document(doc_id: str):
    """
    Obtiene el contenido de un documento específico
    
    Args:
        doc_id: ID del documento
        
    Returns:
        Contenido del documento
    """
    try:
        # Buscar el documento en el sistema de archivos
        docs_dir = Path("app/documentation/processed/docs")
        
        document_path = None
        for doc_type_dir in docs_dir.iterdir():
            if doc_type_dir.is_dir():
                for doc_file in doc_type_dir.glob(f"{doc_id}*"):
                    document_path = doc_file
                    break
            if document_path:
                break
                
        if not document_path:
            raise HTTPException(
                status_code=404,
                detail=f"Documento no encontrado: {doc_id}"
            )
        
        # Leer el documento
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {
            "status": "success",
            "doc_id": doc_id,
            "content": content,
            "format": document_path.suffix[1:],  # Eliminar el punto
            "file_name": document_path.name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo documento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo documento: {str(e)}"
        )