from typing import List, Dict, Optional
import logging
from app.vectorstore.vector_store import VectorStore
from app.vectorstore.common_types import TextType
from .types import SearchRequest, SearchResponse, SearchResult, RelevanceType, SearchStrategy

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, vector_store: VectorStore):
        """
        Inicializa el motor de búsqueda
        
        Args:
            vector_store: Instancia de VectorStore para realizar búsquedas
        """
        self.vector_store = vector_store
        
    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        Realiza una búsqueda según la estrategia solicitada
        
        Args:
            request: Petición de búsqueda con parámetros
            
        Returns:
            SearchResponse con resultados y metadata
        """
        try:
            if request.strategy == SearchStrategy.HYBRID:
                results = self.vector_store.hybrid_search(
                    query=request.query,
                    top_k=request.top_k
                )
            else:
                # Por ahora solo implementamos hybrid_search
                logger.warning(f"Estrategia {request.strategy} no implementada, usando hybrid")
                results = self.vector_store.hybrid_search(
                    query=request.query,
                    top_k=request.top_k
                )
                
            # Convertir resultados al formato SearchResult
            search_results = []
            for result in results:
                if result['score'] < request.min_score:
                    continue
                    
                relevance = self._determine_relevance(result['score'])
                search_results.append(
                    SearchResult(
                        text=result['text'],
                        score=result['score'],
                        metadata=result.get('metadata', {}),
                        section_id=result.get('metadata', {}).get('section_id', ''),
                        relevance=relevance,
                        context=result.get('context')
                    )
                )
                
            return SearchResponse(
                results=search_results,
                metadata={
                    "query": request.query,
                    "strategy": request.strategy
                },
                total_found=len(search_results),
                search_strategy=request.strategy
            )
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            raise
            
    def _determine_relevance(self, score: float) -> RelevanceType:
        """Determina el nivel de relevancia basado en el score"""
        if score >= 0.8:
            return RelevanceType.HIGH
        elif score >= 0.5:
            return RelevanceType.MEDIUM
        return RelevanceType.LOW

    async def search_by_category(
        self, 
        category: str,
        query: str,
        top_k: int = 5
    ) -> SearchResponse:
        """
        Realiza una búsqueda filtrada por categoría
        
        Args:
            category: Categoría a buscar
            query: Query de búsqueda
            top_k: Número máximo de resultados
            
        Returns:
            SearchResponse con resultados filtrados
        """
        request = SearchRequest(
            query=f"{category}: {query}",
            strategy=SearchStrategy.HYBRID,
            filters={"category": category},
            top_k=top_k
        )
        return await self.search(request)

    async def expand_context(
        self,
        result: SearchResult,
        context_window: int = 2
    ) -> Dict:
        """
        Expande el contexto de un resultado recuperando chunks relacionados
        
        Args:
            result: Resultado a expandir
            context_window: Número de chunks antes/después a incluir
            
        Returns:
            Diccionario con contexto expandido
        """
        section_id = result.section_id
        context = result.context or {}
        
        if not section_id:
            return context
            
        try:
            # Obtener chunks de la misma sección
            section_results = self.vector_store.hybrid_search(
                query=result.text,
                top_k=context_window * 2 + 1  # +1 para incluir el chunk actual
            )
            
            # Filtrar y ordenar por posición en la sección
            related_chunks = []
            for chunk in section_results:
                if chunk['id'] != result.metadata.get('id'):
                    related_chunks.append({
                        'text': chunk['text'],
                        'position': chunk.get('position', 0),
                        'score': chunk['score']
                    })
                    
            context['related_chunks'] = sorted(
                related_chunks,
                key=lambda x: x['position']
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error expandiendo contexto: {str(e)}")
            return context