# En app/api/routes/doc.py o donde manejes tus rutas

from fastapi import APIRouter, HTTPException
from app.orchestrator.orchestrator import RAGOrchestrator

router = APIRouter()

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
