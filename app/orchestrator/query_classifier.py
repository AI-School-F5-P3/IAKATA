from typing import Dict, Any, Tuple, List
from enum import Enum
import re
from app.llm.types import TextType

class ConfidenceLevel(Enum):
    """Niveles de confianza para clasificación de consultas"""
    HIGH = "high"       # Score > 0.7
    MEDIUM = "medium"   # Score 0.3-0.7
    LOW = "low"        # Score < 0.3

class QueryClassifier:
    def __init__(self):
        # Keywords específicos de Lean Kata
        self.lean_kata_keywords = {
            # Conceptos fundamentales
            'kata': 3,
            'lean kata': 3,
            'toyota kata': 3,
            'coaching kata': 3,
            'kata de mejora': 3,
            
            # Metodología y procesos
            'mejora continua': 2,
            'pdca': 2,
            'gemba': 2,
            'estandarización': 2,
            'gestión visual': 2,
            
            # Elementos del tablero
            'estado actual': 2,
            'estado objetivo': 2,
            'condición objetivo': 2,
            'reto': 1,
            'obstáculo': 1,
            'hipótesis': 1,
            'experimento': 1,
            'tablero': 1,
            
            # Roles y equipo
            'coach kata': 2,
            'aprendiz kata': 2,
            'equipo de mejora': 1,
            'tribu': 1
        }

    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """
        Determina el nivel de confianza basado en el score.
        
        Args:
            score: Score de confianza (0-1)
            
        Returns:
            ConfidenceLevel correspondiente
        """
        if score > 0.7:
            return ConfidenceLevel.HIGH
        elif score > 0.3:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def classify_query_with_context(self, query: str, conversation_history: List[Dict[str, str]]) -> Tuple[bool, Dict[str, Any]]:
        """
        Clasifica una consulta considerando el historial de conversación.
        
        Args:
            query: Consulta a clasificar
            conversation_history: Lista de mensajes previos
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (es_lean_kata, metadata)
        """
        query_lower = query.lower()
        context_score = 0.0
        
        # Analizar contexto de conversación
        if conversation_history:
            last_messages = conversation_history[-3:]  # Considerar últimos 3 mensajes
            for message in last_messages:
                if message['role'] == 'assistant':
                    # Si hay referencias a Lean Kata en mensajes previos del asistente
                    if any(keyword in message['content'].lower() for keyword in self.lean_kata_keywords):
                        context_score += 0.2  # Aumentar score por contexto
        
        # Analizar keywords en la consulta actual
        keywords_info = self._analyze_keywords(query_lower)
        
        # Combinar scores
        final_score = min(1.0, keywords_info['score'] + context_score)
        
        # Determinar si es Lean Kata basado en el score combinado
        is_lean_kata = keywords_info['is_lean_kata'] or final_score > 0.3
        
        # Metadata con información contextual
        metadata = {
            'text': query,
            'type': TextType.MAIN_CONTENT.value if is_lean_kata else TextType.CONCEPT.value,
            'metadata': {
                'query_type': 'lean_kata' if is_lean_kata else 'general',
                'confidence': final_score,
                'confidence_level': self._get_confidence_level(final_score).value,
                'analysis': {
                    'keywords_found': keywords_info['keywords'],
                    'context_score': context_score
                }
            },
            'section_id': 'lean_kata' if is_lean_kata else 'general'
        }
        
        return is_lean_kata, metadata

    def classify_query(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Método principal de clasificación que no requiere contexto.
        
        Args:
            query: Consulta a clasificar
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (es_lean_kata, metadata)
        """
        query_lower = query.lower()
        
        # Analizar keywords
        keywords_info = self._analyze_keywords(query_lower)
        
        # Determinar si es Lean Kata basado en keywords
        is_lean_kata = keywords_info['is_lean_kata']
        
        # Metadata básica
        metadata = {
            'text': query,
            'type': TextType.MAIN_CONTENT.value if is_lean_kata else TextType.CONCEPT.value,
            'metadata': {
                'query_type': 'lean_kata' if is_lean_kata else 'general',
                'confidence': keywords_info['score'],
                'confidence_level': self._get_confidence_level(keywords_info['score']).value,
                'analysis': {
                    'keywords_found': keywords_info['keywords']
                }
            },
            'section_id': 'lean_kata' if is_lean_kata else 'general'
        }
        
        return is_lean_kata, metadata

    def _analyze_keywords(self, query: str) -> Dict[str, Any]:
        """
        Analiza keywords en la consulta.
        
        Args:
            query: Consulta a analizar
            
        Returns:
            Dict con información de análisis
        """
        keywords_found = []
        total_score = 0
        
        for keyword, weight in self.lean_kata_keywords.items():
            if keyword in query:
                keywords_found.append(keyword)
                total_score += weight
        
        # Normalizar score a rango 0-1
        max_possible_score = sum(weight for weight in self.lean_kata_keywords.values())
        normalized_score = min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0
        
        return {
            'keywords': keywords_found,
            'score': normalized_score,
            'is_lean_kata': len(keywords_found) > 0
        }