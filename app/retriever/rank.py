from typing import List, Dict
import logging
from .types import SearchResult, RelevanceType

logger = logging.getLogger(__name__)

class RankingEngine:
    def __init__(self):
        """Inicializa el motor de ranking"""
        self.category_weights = {
            'Process': 1.2,
            'Challenge': 1.1,
            'Experiment': 1.1,
            'Results': 1.0,
            'Learning': 1.0
        }
        
        self.type_weights = {
            'main_content': 1.2,
            'example': 1.1,
            'procedure': 1.3,
            'concept': 1.0
        }
        
    def rerank(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """
        Reordena los resultados aplicando criterios adicionales
        
        Args:
            results: Lista de resultados a reordenar
            query: Query original para contexto
            
        Returns:
            Lista reordenada de resultados
        """
        try:
            # Calcular scores ajustados
            scored_results = []
            for result in results:
                final_score = self._calculate_final_score(result, query)
                scored_results.append((final_score, result))
                
            # Ordenar por score final
            scored_results.sort(key=lambda x: x[0], reverse=True)
            
            # Actualizar scores y retornar resultados
            reranked_results = []
            for final_score, result in scored_results:
                result.score = final_score
                result.relevance = self._determine_relevance(final_score)
                reranked_results.append(result)
                
            return reranked_results
            
        except Exception as e:
            logger.error(f"Error en reranking: {str(e)}")
            return results
            
    def _calculate_final_score(self, result: SearchResult, query: str) -> float:
        """Calcula el score final considerando múltiples factores"""
        try:
            base_score = result.score
            multiplier = 1.0
            
            # 1. Ajuste por categoría
            category = result.metadata.get('category', '')
            if category in self.category_weights:
                multiplier *= self.category_weights[category]
                
            # 2. Ajuste por tipo de contenido
            content_type = result.metadata.get('type', '')
            if content_type in self.type_weights:
                multiplier *= self.type_weights[content_type]
                
            # 3. Ajuste por longitud
            text_length = len(result.text)
            if text_length < 100:
                multiplier *= 0.8
            elif text_length > 1000:
                multiplier *= 0.9
                
            # 4. Ajuste por coherencia semántica
            if self._check_semantic_relevance(result.text, query):
                multiplier *= 1.2
                
            # 5. Ajuste por contexto
            if result.context and result.context.get('position'):
                position = result.context['position']
                if position.get('is_first'):
                    multiplier *= 1.1
                    
            final_score = base_score * multiplier
            
            # Normalizar entre 0 y 1
            return min(max(final_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculando score final: {str(e)}")
            return result.score
            
    def _check_semantic_relevance(self, text: str, query: str) -> bool:
        """Verifica relevancia semántica básica"""
        # Implementación simple, podría mejorarse con NLP
        query_terms = query.lower().split()
        text_lower = text.lower()
        
        found_terms = sum(1 for term in query_terms if term in text_lower)
        return found_terms >= len(query_terms) * 0.5
        
    def _determine_relevance(self, score: float) -> RelevanceType:
        """Determina nivel de relevancia basado en score"""
        if score >= 0.8:
            return RelevanceType.HIGH
        elif score >= 0.5:
            return RelevanceType.MEDIUM
        return RelevanceType.LOW