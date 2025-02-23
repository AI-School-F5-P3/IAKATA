import asyncio
import sys
import os
from pathlib import Path
import logging

# Para correr este archivo usar "python -m app.test_chat_4" desde la carpera app

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar desde rutas relativas
from .llm.types import LLMRequest, ResponseType
from .llm.gpt import LLMModule

async def chat_session():
    """Maneja una sesión de chat interactiva por consola"""
    try:
        # Inicializar el módulo LLM
        llm = LLMModule()
        print("\n=== Chat Iniciado ===")
        print("Puedes hacer cualquier pregunta. El sistema detectará si está relacionada con Lean Kata.")
        print("Para salir, escribe 'salir' o 'exit'\n")
        
        # Mantener historial de conversación
        conversation_history = []
        
        while True:
            # Obtener input del usuario
            user_input = input("\nTú: ").strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                break
                
            if not user_input:
                continue
                
            try:
                # Crear un LLMRequest apropiado
                request = LLMRequest(
                    query=user_input,
                    response_type=ResponseType.CHAT,
                    context={
                        'conversation_history': conversation_history
                    },
                    temperature=0.7,
                    language="es"
                )
                
                # Procesar el mensaje
                response = await llm.process_request(request)
                
                # Mostrar la respuesta
                print(f"\nAsistente: {response.content}")
                
                # Actualizar historial de conversación
                conversation_history.append({
                    'role': 'user',
                    'content': user_input
                })
                conversation_history.append({
                    'role': 'assistant',
                    'content': response.content
                })
                
                # Limitar el historial para evitar que crezca indefinidamente
                if len(conversation_history) > 10:
                    conversation_history = conversation_history[-10:]
                
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Intenta hacer otra pregunta.")
                
        print("\n=== Chat Finalizado ===")
        
    except Exception as e:
        print(f"\nError en la sesión de chat: {str(e)}")

async def main():
    """Función principal"""
    try:
        await chat_session()
    except Exception as e:
        print(f"Error principal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Ejecutar el loop de eventos
    asyncio.run(main())