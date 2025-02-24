from fastapi import APIRouter, Depends, HTTPException
from models.request_models import DocumentRequest
from models.response_models import DocumentResponse
from core.setup import AIComponents

router = APIRouter(prefix="/document", tags=["document"])

@router.post("/", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest, ai: AIComponents = Depends()):
    try:
        document = await ai.orchestrator.generate_document(
            content=request.content,
            template_type=request.template_type,
            metadata=request.metadata
        )
        return DocumentResponse(
            status="success",
            document=document
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))