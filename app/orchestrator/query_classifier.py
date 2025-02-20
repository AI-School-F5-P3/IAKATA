from typing import Dict, Any, Tuple
import sys
from pathlib import Path


# Get the absolute path of the project root
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from app.llm.types import TextType

class QueryClassifier:
    """
    Clasifica las consultas diferenciando entre Lean Kata y consultas generales.
    """
    
    def __init__(self):
        # Keywords específicos de Lean Kata
        self.lean_kata_keywords = {
            # Conceptos fundamentales
            'kata', 'lean kata', 'toyota kata', 
            'coaching kata', 'kata de mejora',
            
            # Metodología y procesos
            'mejora continua', 'pdca', 'gemba',
            'estandarización', 'gestión visual',
            
            # Elementos del tablero
            'estado actual', 'estado objetivo', 
            'condición objetivo', 'reto', 
            'obstáculo', 'hipótesis',
            'experimento', 'tablero',
            
            # Roles y equipo
            'coach kata', 'aprendiz kata',
            'equipo de mejora', 'tribu'
        }
    
    def classify_query(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Clasifica una consulta como Lean Kata o general.
        
        Args:
            query: La consulta del usuario
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (es_lean_kata, metadata)
        """
        query_lower = query.lower()
        
        # Detectar keywords de Lean Kata
        keywords_found = [kw for kw in self.lean_kata_keywords if kw in query_lower]
        is_lean_kata = len(keywords_found) > 0
        
        # Calcular confianza de la clasificación
        confidence = self._calculate_confidence(keywords_found)
        
        # Construir metadata consistente
        metadata = {
            'text': query,  # Mantener el texto original
            'type': TextType.MAIN_CONTENT.value if is_lean_kata else TextType.CONCEPT.value,
            'metadata': {
                'query_type': 'lean_kata' if is_lean_kata else 'general',
                'confidence': confidence,
                'keywords_found': keywords_found if is_lean_kata else []
            },
            'section_id': 'lean_kata' if is_lean_kata else 'general'
        }
        
        return is_lean_kata, metadata
    
    def _calculate_confidence(self, keywords_found: list) -> float:
        """
        Calcula el nivel de confianza en la clasificación.
        
        Args:
            keywords_found: Lista de keywords de Lean Kata encontrados
            
        Returns:
            float: Nivel de confianza entre 0 y 1
        """
        if not keywords_found:
            return 0.9  # Alta confianza para consultas generales
            
        # Para consultas Lean Kata, la confianza aumenta con más keywords
        keyword_confidence = min(0.5 + (len(keywords_found) * 0.1), 0.9)
        return keyword_confidence