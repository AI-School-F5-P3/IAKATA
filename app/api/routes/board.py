from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.api.services.rag_services import rag_response, store_context_db

from app.api.models import FormData, ResponseOutput, Context

router = APIRouter()

@router.post("/ai")
async def improve_with_ai(data: FormData): # -> ResponseOutput:
    try:
        response = await rag_response(data)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "RAG response generated successfully",
                "data": response,
            }
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error: {str(e)}"
            )

# obtener info del proyecto
# @router.post("/store-context")
# async def store_context(data: Context):
#     try:
#         success = store_context_db(data)
#         if not success:
#             raise HTTPException(status_code=500, detail="Fail to store")
#         return {"message": "Ok"}
#     except Exception as e:
#         print(f"Error storing context: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
