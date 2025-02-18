import asyncio
import sys
import os
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio raíz al PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from app.orchestrator.orchestrator import RAGOrchestrator
from app.vectorstore.vector_store import VectorStore
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.chat.manager import ChatManager

async def initialize_components():
    """Inicializa todos los componentes necesarios"""
    try:
        print("Inicializando componentes...")
        
        # Calcular rutas absolutas
        vectors_dir = root_dir / "app" / "vectorstore" / "processed" / "vectors"
        
        print(f"Buscando vectores en: {vectors_dir}")
        
        # Verificar que existen los archivos necesarios
        required_files = ["faiss.index", "metadata.npy", "chunk_data.json"]
        missing_files = [f for f in required_files if not (vectors_dir / f).exists()]
        
        if missing_files:
            print(f"ADVERTENCIA: Faltan los siguientes archivos: {missing_files}")
            print(f"Por favor, asegúrate de que existan en: {vectors_dir}")
            return None
            
        # Inicializar Vector Store y cargar vectores
        vector_store = VectorStore()
        vector_store.load(vectors_dir)
        
        print("Vector store inicializado")
        
        # Inicializar LLM
        llm = LLMModule()
        print("LLM módulo inicializado")
        
        # Inicializar validador
        validator = ResponseValidator()
        print("Validador inicializado")
        
        # Inicializar el orquestador
        orchestrator = RAGOrchestrator(
            vector_store=vector_store,
            llm=llm,
            validator=validator
        )
        print("Orquestador inicializado")
        
        # Inicializar el gestor de chat
        chat_manager = ChatManager(
            orchestrator=orchestrator,
            context_window_size=10
        )
        print("Chat manager inicializado")
        
        return chat_manager
        
    except Exception as e:
        print(f"Error inicializando componentes: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        raise

async def chat_session(chat_manager: ChatManager):
    """Maneja una sesión de chat interactiva"""
    try:
        if not chat_manager:
            print("No se pudo inicializar el chat manager")
            return
            
        # Crear una nueva sesión
        session_id = await chat_manager.create_chat_session(
            user_id="console_user",
            metadata={"source": "cli"}
        )
        
        print("\n=== Chat de LeanKata Iniciado ===")
        print("Este asistente te ayudará con la metodología LeanKata.")
        print("Puedes preguntar sobre:")
        print("- Conceptos y principios de LeanKata")
        print("- Cómo implementar la metodología")
        print("- Ayuda con los tableros y experimentos")
        print("\nEscribe 'salir' para terminar la conversación\n")
        
        while True:
            try:
                # Obtener input del usuario
                user_input = input("Usuario: ").strip()
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    break
                    
                if not user_input:
                    continue
                    
                # Procesar el mensaje
                response = await chat_manager.process_message(
                    session_id=session_id,
                    content=user_input
                )
                
                # Mostrar la respuesta
                print(f"\nAsistente: {response.message.content}\n")
                
            except Exception as e:
                print(f"\nError procesando mensaje: {str(e)}")
                print("Continuando con el siguiente mensaje...\n")
                
        # Cerrar la sesión al terminar
        await chat_manager.close_chat_session(session_id)
        print("\n=== Chat Finalizado ===\n")
        
    except Exception as e:
        print(f"\nError en la sesión de chat: {str(e)}")
        print(f"Tipo de error: {type(e)}\n")

async def main():
    """Función principal"""
    try:
        # Inicializar componentes
        chat_manager = await initialize_components()
        
        if chat_manager:
            # Iniciar sesión de chat
            await chat_session(chat_manager)
        else:
            print("No se pudo iniciar el chat debido a archivos faltantes")
        
    except Exception as e:
        print(f"Error principal: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Ejecutar el loop de eventos
    asyncio.run(main())