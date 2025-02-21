from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, max_history: int = 5):
        """
        Inicializa el gestor de conversaciones.
        
        Args:
            max_history: Número máximo de mensajes a mantener en el historial
        """
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history = max_history

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de una sesión.
        
        Args:
            session_id: ID único de la sesión
            
        Returns:
            Lista de mensajes de la conversación
        """
        return self.conversations.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Añade un mensaje al historial.
        
        Args:
            session_id: ID de la sesión
            role: 'user' o 'assistant'
            content: Contenido del mensaje
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.conversations[session_id].append(message)
        
        # Mantener solo los últimos max_history mensajes
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]

    def build_prompt(self, session_id: str, current_query: str) -> str:
        """
        Construye el prompt incluyendo el contexto histórico.
        
        Args:
            session_id: ID de la sesión
            current_query: Consulta actual del usuario
            
        Returns:
            Prompt completo con contexto
        """
        context = self._build_conversation_context(session_id)
        
        prompt = f"""Contexto de la conversación anterior:

{context}

Consulta actual: {current_query}

Basándote en el contexto de la conversación anterior, proporciona una respuesta relevante y coherente."""

        return prompt

    def _build_conversation_context(self, session_id: str) -> str:
        """
        Construye el contexto de la conversación.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Contexto formateado
        """
        if session_id not in self.conversations:
            return ""
            
        context = []
        for msg in self.conversations[session_id]:
            prefix = "Usuario" if msg['role'] == 'user' else "Asistente"
            context.append(f"{prefix}: {msg['content']}")
            
        return "\n".join(context)

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Obtiene un resumen de la sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Diccionario con el resumen de la sesión
        """
        if session_id not in self.conversations:
            return {
                'messages_count': 0,
                'session_duration': 0,
                'last_interaction': None
            }
            
        messages = self.conversations[session_id]
        
        if not messages:
            return {
                'messages_count': 0,
                'session_duration': 0,
                'last_interaction': None
            }
            
        first_msg_time = datetime.fromisoformat(messages[0]['timestamp'])
        last_msg_time = datetime.fromisoformat(messages[-1]['timestamp'])
        
        return {
            'messages_count': len(messages),
            'session_duration': (last_msg_time - first_msg_time).total_seconds(),
            'last_interaction': last_msg_time.isoformat()
        }

    def clear_session(self, session_id: str) -> None:
        """
        Limpia el historial de una sesión.
        
        Args:
            session_id: ID de la sesión a limpiar
        """
        if session_id in self.conversations:
            del self.conversations[session_id]