from fastapi import APIRouter, Depends, HTTPException, Header
from models.request_models import ImproveRequest
from models.response_models import ImproveResponse
from core.setup import AIComponents

router = APIRouter(prefix="/improve", tags=["improve"])

@router.post("/", response_model=ImproveResponse)
async def improve_content(
    request: ImproveRequest,
    authorization: str = Header(None),  # Recibir el token como header
    ai: AIComponents = Depends()
):
    try:
        improved = await ai.orchestrator.improve_content(
            content=request.content,
            content_type=request.content_type,
            context=request.context,
            token=authorization  # Pasar el token al orquestador
        )
        return ImproveResponse(
            status="success",
            improved_content=improved
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
