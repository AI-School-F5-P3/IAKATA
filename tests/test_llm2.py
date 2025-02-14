import sys
import os
import asyncio
from app.llm.gpt import LLMModule
from app.llm.types import LLMRequest, ResponseType

# Agregar la carpeta raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "llm")))

async def main():
    llm = LLMModule()  # Inicializa el módulo
    
    request = LLMRequest(
        query="¿Cuál es la capital de Francia?",
        response_type=ResponseType.CHAT
    )
    
    response = await llm.process_request(request)
    
    print("Respuesta de ChatGPT:", response.content)

# Ejecutar la prueba
asyncio.run(main())
