import httpx
from typing import Dict, Any
from app.api.models import FormData
from app.retriever.retriever import RetrieverSystem
from app.retriever.types import BoardSection, RetrieverResponse
from app.orchestrator.orchestrator import RAGOrchestrator
from app.retriever.search import SearchEngine
from app.llm.types import ResponseType, LLMResponse
from app.vectorstore.vector_store import VectorStore
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Configurar rutas
BASE_DIR = Path(__file__).resolve().parent.parent
VECTORS_DIR = BASE_DIR / "vectorstore" / "processed" / "vectors"

try:
    # Inicializar componentes
    vector_store = VectorStore()
    vector_store.load(VECTORS_DIR)
    
    llm = LLMModule()
    validator = ResponseValidator()
    
    # Inicializar sistemas principales
    retriever_system = RetrieverSystem(vector_store)
    orchestrator = RAGOrchestrator(
        vector_store=vector_store,
        llm=llm,
        validator=validator,
    )
    
    logger.info("Componentes RAG inicializados correctamente")
    
except Exception as e:
    logger.error(f"Error inicializando componentes RAG: {str(e)}")
    raise

async def rag_response(data: FormData) -> Dict[str, Any]:
    """
    Procesa una solicitud RAG y retorna una respuesta.
    
    Args:
        data: Datos del formulario con la consulta
        
    Returns:
        Dict con la respuesta procesada
    """
    try:
        data_dict = data.model_dump()
        type_input = data_dict['id'][0]
        
        # Determinar tipo de sección y respuesta
        section_type = "challenge" if type_input == 'R' else "general"
        
        # Obtener respuesta del orquestador
        response: LLMResponse = await orchestrator.validate_board_section(
            category=section_type,
            content=data_dict['description']
        )
        
        # Procesar respuesta
        suggestion = response.content if isinstance(response.content, str) else str(response.content)
        
        # Enriquecer respuesta con metadata si existe
        result = {
            "description": f"sugerencia: {suggestion}",
            "metadata": response.metadata if response.metadata else {}
        }
        
        logger.info(f"Respuesta RAG generada para sección tipo: {section_type}")
        return result
        
    except Exception as e:
        logger.error(f"Error procesando respuesta RAG: {str(e)}")
        raise

async def store_context_db(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Almacena contexto en la base de datos.
    Por implementar completamente.
    
    Args:
        data: Datos de contexto a almacenar
        
    Returns:
        Dict con confirmación
    """
    try:
        # TODO: Implementar almacenamiento real en BD
        logger.info("Solicitud de almacenamiento de contexto recibida")
        return {"response": "stored"}
        
    except Exception as e:
        logger.error(f"Error almacenando contexto: {str(e)}")
        raise