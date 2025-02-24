from fastapi import APIRouter, Depends, HTTPException
from models.request_models import SearchRequest
from models.response_models import SearchResponse
from core.setup import AIComponents

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/", response_model=SearchResponse)
async def search_content(request: SearchRequest, ai: AIComponents = Depends()):
    try:
        results = await ai.orchestrator.search(
            query=request.query,
            filters=request.filters,
            limit=request.limit
        )
        return SearchResponse(
            status="success",
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))