from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.api.services.rag_services import rag_response, store_context_db

from app.api.models import FormData, ResponseOutput, Context

router = APIRouter()

@router.post("/ai")
async def improve_with_ai(data: FormData): # -> ResponseOutput:
    try:
        print(data)
        response = await rag_response(data)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "RAG response generated successfully",
                "data": response,
            }
        )
    except Exception as e:
            # Logging adecuado para la excepción
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en improve_with_ai: {str(e)}")
            
            # Retornar error en formato correcto
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error en la api: {str(e)}"
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
