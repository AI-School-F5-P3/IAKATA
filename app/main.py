from pathlib import Path
from app.documentation.generator import DocumentGenerator
from app.documentation.template_manager import TemplateStyleManager
from app.documentation.storage import DocumentStorage
from app.orchestrator.orchestrator import RAGOrchestrator
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.vectorstore.vector_store import VectorStore
from app.llm.types import ResponseType
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Importar el router de board
try:
    from app.api.routes.board import router as board_router
    has_board_router = True
except ImportError:
    has_board_router = False
    print("ADVERTENCIA: No se pudo importar el router de board. Definiendo endpoint directamente.")


class AIRequest(BaseModel):
    idForm: str
    description: str
    type: str


def configure_orchestrator() -> RAGOrchestrator:
    """
    Configura e inicializa el orquestador con todos sus componentes
    """
    try:
        # Inicializar VectorStore y cargar datos existentes
        vector_store = VectorStore()
        vector_store_path = Path("app/vectorstore/processed/vectors")
        if vector_store_path.exists():
            print(f"Cargando datos del vector store desde {vector_store_path}")
            vector_store.load(vector_store_path)
        else:
            print("ADVERTENCIA: No se encontró directorio del vector store")
            
        # Resto de componentes
        llm = LLMModule()
        validator = ResponseValidator()
        template_manager = TemplateStyleManager()
        doc_generator = DocumentGenerator(llm)
        doc_storage = DocumentStorage(Path("./docs"))
        
        # Crear orquestador
        orchestrator = RAGOrchestrator(
            vector_store=vector_store,
            llm=llm,
            validator=validator,
            doc_generator=doc_generator,
            template_manager=template_manager,
            doc_storage=doc_storage
        )
        
        return orchestrator
        
    except Exception as e:
        print(f"Error configurando el orquestador: {str(e)}")
        raise


# Inicializar el orquestrador
orchestrator = configure_orchestrator()

app = FastAPI()

# Configurar CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Origen de tu frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir el router de board si está disponible
if has_board_router:
    app.include_router(board_router, prefix="/api/routes/board", tags=["board"])
    print("Router de board montado en /api/routes/board")
else:
    # Definir el endpoint directamente si no hay router disponible
    @app.post("/api/routes/board/ai")
    async def improve_with_ai(request: AIRequest):
        """
        Procesa una solicitud para mejorar texto con IA
        """
        try:
            # Determinar el tipo de respuesta basado en el parámetro 'type'
            response_type = ResponseType.CHAT if request.type == "concise" else ResponseType.VALIDATION
            
            # Contexto para el orquestrador
            context = {
                "response_type": request.type,
                "idForm": request.idForm
            }
            
            # Usar el método process_board_request del orquestrador
            response = await orchestrator.process_board_request(
                section_type=request.idForm,
                content=request.description,
                context=context
            )
            
            # Extraer el contenido de la respuesta
            improved_text = response.content
            
            return {"data": {"description": improved_text}}
        except Exception as e:
            print(f"Error en /api/routes/board/ai: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error en el procesamiento: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "FastAPI está funcionando correctamente"}