import asyncio
import sys
import os
from pathlib import Path

# Añadir el directorio raíz al PYTHONPATH
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Importar con el nombre correcto del archivo
from app.orchestrator.orchestrator import RAGOrchestrator
from app.vectorstore.vector_store import VectorStore
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.chat.manager import ChatManager

async def initialize_components():
    """Inicializa todos los componentes necesarios"""
    try:
        print("Inicializando componentes...")
        
        # Inicializar componentes base con configuración mínima
        vector_store = VectorStore()
        print("Vector store inicializado")
        
        llm = LLMModule()
        print("LLM módulo inicializado")
        
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
        # Crear una nueva sesión
        session_id = await chat_manager.create_chat_session(
            user_id="console_user",
            metadata={"source": "cli"}
        )
        
        print("\n=== Chat Iniciado ===")
        print("Escribe 'salir' para terminar la conversación\n")
        
        while True:
            # Obtener input del usuario
            user_input = input("Usuario: ").strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                break
                
            if not user_input:
                continue
                
            try:
                # Procesar el mensaje
                response = await chat_manager.process_message(
                    session_id=session_id,
                    content=user_input
                )
                
                # Mostrar la respuesta
                print(f"\nAsistente: {response.message.content}\n")
                
            except Exception as e:
                print(f"\nError procesando mensaje: {str(e)}")
                print(f"Tipo de error: {type(e)}\n")
                
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
        
        # Iniciar sesión de chat
        await chat_session(chat_manager)
        
    except Exception as e:
        print(f"Error principal: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Ejecutar el loop de eventos
    asyncio.run(main())