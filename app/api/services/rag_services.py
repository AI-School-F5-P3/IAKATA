import httpx
from app.api.models import FormData
from app.retriever.retriever import RetrieverSystem
from app.retriever.types import BoardSection, RetrieverResponse
from app.retriever.search import SearchEngine
from app.llm.types import ResponseType
from app.vectorstore.vector_store import VectorStore
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.llm.types import ResponseType
import asyncio

vector_store = VectorStore()
retriever_system = RetrieverSystem(vector_store)
llm = LLMModule()
validator = ResponseValidator()

def get_orchestrator():
    from app.orchestrator.orchestrator import RAGOrchestrator
    global orchestrator
    if 'orchestrator' not in globals():
        orchestrator = RAGOrchestrator(
            vector_store=vector_store,
            llm=llm,
            validator=validator,
        )
    return orchestrator

CATEGORIAS = {
    "RE": "challenge",
    "TA": "target",
    "EX": "experiment",
    "HI": "hypothesis"
}



async def rag_response(data: FormData) -> str:
    data_dict = data.model_dump()
    
    # Obtener el tipo de formulario
    form_id = data_dict.get('idForm')
    description = data_dict.get('description')
    
    # Determinar el tipo de contenido basado en el formulario
    section_type = CATEGORIAS.get(form_id)
    
    # Agregar instrucciones específicas según el tipo de formulario
    instruction = ""
    if form_id == "PR":  # Proceso
        instruction = "Proporciona 2-3 oraciones concisas que definan el alcance y objetivo del proceso. Sé específico y directo."
    elif form_id == "RE":  # Reto
        instruction = "Proporciona una definición clara y concisa del reto en 1-2 oraciones. Enfócate en el problema principal."
    elif form_id == "HI":  # Hipótesis
        instruction = "Formula una hipótesis clara y comprobable en 1-2 oraciones. Debe seguir el formato 'Si... entonces...'."
    elif form_id == "EX":  # Experimento
        instruction = "Describe brevemente un experimento simple y rápido en 2-3 oraciones. Enfócate en qué hacer, cómo medirlo y cuándo."
    elif form_id == "TA":  # Target
        instruction = "Define un objetivo específico, medible y con plazo en 1-2 oraciones. Incluye métricas concretas."
    
    # Incluir la instrucción en la consulta
    orchestrator = get_orchestrator()
    
    enhanced_request = f"{description}\n\n[INSTRUCCIÓN PARA IA: {instruction} Limita tu respuesta a máximo 50 palabras.]"
    
    response = await orchestrator.process_board_request(
        section_type, 
        content=enhanced_request, 
        context={"response_type": "concise"}
    )
    
    response_dict = response.model_dump()
    print("-------------------------------")
    print(response_dict['content'])
    
    return {"description": f"{response_dict['content']}"}


async def store_context_db(data: dict) -> str:
    return {f"response"}

