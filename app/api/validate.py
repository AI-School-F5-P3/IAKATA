from fastapi import APIRouter, Depends, HTTPException
from models.request_models import ValidationRequest
from models.response_models import ValidationResponse
from core.setup import AIComponents

router = APIRouter(prefix="/validate", tags=["validate"])

@router.post("/", response_model=ValidationResponse)
async def validate_content(request: ValidationRequest, ai: AIComponents = Depends()):
    try:
        validation = await ai.orchestrator.validate_content(
            content=request.content,
            validation_type=request.validation_type,
            criteria=request.criteria
        )
        return ValidationResponse(
            status="success",
            **validation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))