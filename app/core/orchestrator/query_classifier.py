from typing import Dict, Any, Tuple, List
from enum import Enum
import re
from core.llm.types import TextType

class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class QueryClassifier:
    def __init__(self):
        # Keywords específicos de Lean Kata
        self.lean_kata_keywords = {
            # Conceptos fundamentales
            'kata': 3,  # Peso más alto para términos core
            'lean kata': 3,
            'toyota kata': 3,
            'coaching kata': 3,
            'kata de mejora': 3,
            
            # Metodología y procesos
            'mejora continua': 2,  # Peso medio para conceptos metodológicos
            'pdca': 2,
            'gemba': 2,
            'estandarización': 2,
            'gestión visual': 2,
            
            # Elementos del tablero
            'estado actual': 2,
            'estado objetivo': 2,
            'condición objetivo': 2,
            'reto': 1,  # Peso menor para términos más generales
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

        # Patrones de estructura de pregunta
        self.question_patterns = {
            'specific': [
                r'^cómo (?:puedo|podemos|debo|debemos)',
                r'^cuál es (?:la|el) (?:mejor|correcta|correcto)',
                r'^qué pasos debo',
                r'^cuáles son los elementos'
            ],
            'ambiguous': [
                r'^qué es',
                r'^por qué',
                r'^para qué',
                r'^cuando'
            ]
        }

        # Indicadores de contexto
        self.context_indicators = {
            'process': ['implementar', 'aplicar', 'realizar', 'ejecutar', 'desarrollar'],
            'learning': ['aprender', 'entender', 'comprender', 'estudiar'],
            'problem': ['resolver', 'solucionar', 'mejorar', 'optimizar']
        }

    def classify_query(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Clasifica una consulta con análisis avanzado.
        """
        query_lower = query.lower()
        
        # 1. Análisis de keywords
        keywords_info = self._analyze_keywords(query_lower)
        
        # 2. Análisis de estructura
        structure_score = self._analyze_structure(query_lower)
        
        # 3. Análisis de contexto
        context_score = self._analyze_context(query_lower)
        
        # 4. Cálculo de confianza combinada
        total_score = self._calculate_combined_confidence(
            keywords_info['score'],
            structure_score,
            context_score
        )
        
        # 5. Determinar nivel de confianza
        confidence_level = self._get_confidence_level(total_score)
        
        # Determinar si es Lean Kata
        is_lean_kata = keywords_info['is_lean_kata'] or total_score > 0.7

        # Construir metadata enriquecida
        metadata = {
            'text': query,
            'type': TextType.MAIN_CONTENT.value if is_lean_kata else TextType.CONCEPT.value,
            'metadata': {
                'query_type': 'lean_kata' if is_lean_kata else 'general',
                'confidence': total_score,
                'confidence_level': confidence_level.value,
                'keywords_found': keywords_info['keywords'],
                'structure_analysis': {
                    'score': structure_score,
                    'patterns_matched': keywords_info['patterns']
                },
                'context_analysis': {
                    'score': context_score,
                    'indicators_found': keywords_info['context']
                }
            },
            'section_id': 'lean_kata' if is_lean_kata else 'general'
        }

        return is_lean_kata, metadata

    def _analyze_keywords(self, query: str) -> Dict[str, Any]:
        """
        Analiza las keywords encontradas y su relevancia.
        """
        keywords_found = []
        patterns_matched = []
        context_indicators = []
        total_weight = 0
        max_possible_weight = sum(max(self.lean_kata_keywords.values()) for _ in range(3))  # Asumimos 3 keywords como máximo ideal

        # Buscar keywords con peso
        for keyword, weight in self.lean_kata_keywords.items():
            if keyword in query:
                keywords_found.append(keyword)
                total_weight += weight

        # Normalizar score de keywords
        keyword_score = min(total_weight / max_possible_weight, 1.0)

        return {
            'is_lean_kata': len(keywords_found) > 0,
            'keywords': keywords_found,
            'patterns': patterns_matched,
            'context': context_indicators,
            'score': keyword_score
        }

    def _analyze_structure(self, query: str) -> float:
        """
        Analiza la estructura de la pregunta.
        """
        structure_score = 0.5  # Score base

        # Verificar patrones específicos
        for pattern in self.question_patterns['specific']:
            if re.search(pattern, query):
                structure_score = min(structure_score + 0.2, 1.0)
                break

        # Penalizar patrones ambiguos
        for pattern in self.question_patterns['ambiguous']:
            if re.search(pattern, query):
                structure_score = max(structure_score - 0.1, 0.0)
                break

        # Bonus por longitud y complejidad
        words = query.split()
        if len(words) > 8:  # Preguntas más elaboradas
            structure_score = min(structure_score + 0.1, 1.0)

        return structure_score

    def _analyze_context(self, query: str) -> float:
        """
        Analiza el contexto de la pregunta.
        """
        context_score = 0.5  # Score base
        indicators_found = 0

        # Buscar indicadores de contexto
        for category, indicators in self.context_indicators.items():
            for indicator in indicators:
                if indicator in query:
                    indicators_found += 1
                    context_score = min(context_score + 0.15, 1.0)
                    break  # Solo contar una vez por categoría

        # Ajustar score basado en cantidad de indicadores
        if indicators_found == 0:
            context_score = max(context_score - 0.2, 0.0)
        elif indicators_found > 2:
            context_score = min(context_score + 0.1, 1.0)

        return context_score

    def _calculate_combined_confidence(
        self,
        keyword_score: float,
        structure_score: float,
        context_score: float
    ) -> float:
        """
        Calcula la confianza combinada con pesos diferentes.
        """
        # Pesos para cada componente
        weights = {
            'keyword': 0.5,    # Keywords son el factor más importante
            'structure': 0.3,  # Estructura tiene peso medio
            'context': 0.2     # Contexto tiene el menor peso
        }

        combined_score = (
            keyword_score * weights['keyword'] +
            structure_score * weights['structure'] +
            context_score * weights['context']
        )

        return round(combined_score, 2)

    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """
        Determina el nivel de confianza basado en el score.
        """
        if score < 0.4:
            return ConfidenceLevel.LOW
        elif score < 0.7:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.HIGH