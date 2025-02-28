from pathlib import Path
from app.documentation.generator import DocumentGenerator
from app.documentation.template_manager import TemplateStyleManager
from app.documentation.storage import DocumentStorage
from app.orchestrator.orchestrator import RAGOrchestrator
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.vectorstore.vector_store import VectorStore
from app.config.settings import get_settings

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
        settings = get_settings()
        doc_storage = DocumentStorage(settings.DOCS_DIR)
        
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

# Donde inicialices tu aplicación
orchestrator = configure_orchestrator()