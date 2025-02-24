from pathlib import Path
from core.orchestrator.orchestrator import RAGOrchestrator
from vectorstore.vector_store import VectorStore
from llm.gpt import LLMModule
from llm.validator import ResponseValidator
from documentation.generator import DocumentGenerator
from documentation.templates import TemplateManager
from documentation.storage import DocumentStorage
from chat.manager import ChatManager
from chat.session import SessionManager
from config import get_settings, CustomLogger
from core.auth import HeaderValidator

class AIComponents:
    _instance = None
    logger = CustomLogger("app.core.setup")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIComponents, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.settings = get_settings()
            self._initialize_components()
            self._initialized = True
            
    def _initialize_components(self):
        """
        Inicializa todos los componentes y el orquestador
        """
        try:
            self.logger.process_start("initialize_components")
            
            # Inicializar componentes básicos
            self._initialize_basic_components()
            
            # Crear orquestador
            self.orchestrator = self._configure_orchestrator()
            
            # Inicializar managers que dependen del orchestrator
            self._initialize_managers()
            
            self.logger.process_end("initialize_components")
            
        except Exception as e:
            self.logger.error_with_context(e, {"component": "setup"})
            raise

    def _initialize_basic_components(self):
        """Inicializa componentes que no dependen de otros"""
        # Inicializar VectorStore
        self.vector_store = VectorStore()
        vector_store_path = self.settings.VECTOR_STORE_DIR
        if vector_store_path.exists():
            self.logger.info(f"Cargando datos del vector store desde {vector_store_path}")
            self.vector_store.load(vector_store_path)
        else:
            self.logger.warning("No se encontró directorio del vector store")

        # Inicializar componentes independientes
        self.llm = LLMModule()
        self.validator = ResponseValidator()
        self.template_manager = TemplateManager()
        self.doc_generator = DocumentGenerator(self.llm)
        self.doc_storage = DocumentStorage(Path("./docs"))

    def _configure_orchestrator(self) -> RAGOrchestrator:
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
            template_manager = TemplateManager()
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
        
    def _initialize_managers(self):
        """Inicializa los managers que dependen del orchestrator"""
        try:
            # Los managers ahora son propiedades que se crean bajo demanda
            self._chat_manager = None
            self._session_manager = None
        except Exception as e:
            self.logger.error_with_context(e, {"component": "managers"})
            raise

    @property
    def chat_manager(self) -> ChatManager:
        """Obtiene o crea el ChatManager"""
        if self._chat_manager is None:
            self._chat_manager = ChatManager(orchestrator=self.orchestrator)
        return self._chat_manager

    @property
    def session_manager(self) -> SessionManager:
        """Obtiene o crea el SessionManager"""
        if self._session_manager is None:
            self._session_manager = SessionManager(orchestrator=self.orchestrator)
        return self._session_manager

def get_ai_components() -> AIComponents:
    """Función helper para obtener la instancia de AIComponents"""
    return AIComponents()