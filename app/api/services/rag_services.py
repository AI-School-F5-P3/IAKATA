import httpx
from app.api.models import FormData
from app.retriever.retriever import RetrieverSystem
from app.retriever.types import BoardSection, RetrieverResponse
from app.orchestrator.orchestrator import RAGOrchestrator
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

orchestrator = RAGOrchestrator(
    vector_store=vector_store,
    llm=llm,
    validator=validator,
)

CATEGORIAS = {
    "RE": "challenge",
    "TA": "target",
    "EX": "experiment",
    "HI": "hypothesis"
}

async def rag_response(data: FormData) -> str:
    data = data.model_dump()
    # section = BoardSection(content=data["description"], metadata={"category": section_type})
    # response = await retriever_system.process_content(section)
    # response = await orchestrator.process_query(data['description'], ResponseType.SUGGESTION)
    section = CATEGORIAS.get(data['idForm'])
    response = await orchestrator.process_board_request(section, content=data['description'], context={})
    response = response.model_dump()
    print("-------------------------------")
    print(response['content'])
    return {"description": f"{response['content']}"}


async def store_context_db(data: dict) -> str:
    return {f"response"}

