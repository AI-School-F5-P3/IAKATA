import httpx

async def rag_response(data: dict) -> str:
    return {"description": f"sugerencia: {data.description}"}


async def store_context_db(data: dict) -> str:
    return {f"response"}