from typing import Dict, Any, List
from app.retriever.types import (
    BoardSection,
    SearchQuery,
    RankingConfig,
    FilterConfig,
    RetrieverResponse
)
from app.retriever.search import SearchEngine
from app.retriever.rank import RankEngine
from app.retriever.filter import FilterSystem
from app.llm.types import ResponseType

class RetrieverSystem:
    """
    Sistema principal de recuperación que coordina búsqueda, 
    ranking y filtrado
    """
    
    def __init__(
        self,
        vector_store,
        ranking_config: RankingConfig = RankingConfig(),
        filter_config: FilterConfig = FilterConfig()
    ):
        self.search_engine = SearchEngine(vector_store)
        self.rank_engine = RankEngine(ranking_config)
        self.filter_system = FilterSystem(filter_config)

    async def process_content(
        self,
        board_content: BoardSection,
        max_results: int = 5
    ) -> RetrieverResponse:
        """
        Procesa contenido del tablero y retorna resultados relevantes
        """
        try:
            # 1. Preparar query
            search_query = SearchQuery(
                text=board_content.content,
                metadata=board_content.metadata,
                max_results=max_results
            )
            
            # 2. Realizar búsqueda
            search_results = await self.search_engine.search(search_query)
            
            # 3. Obtener keywords para ranking
            keywords = self.search_engine.get_keywords_from_metadata(board_content.metadata)
            
            # 4. Rankear resultados
            ranked_results = self.rank_engine.rank_results(
                results=search_results,
                keywords=keywords,
                metadata=board_content.metadata
            )
            
            # 5. Filtrar y procesar resultados
            filtered_response = self.filter_system.filter_results(
                results=ranked_results,
                metadata=board_content.metadata
            )
            
            # 6. Construir respuesta final
            response = RetrieverResponse(
                response_type=filtered_response["response_type"],
                search_results=filtered_response["search_results"],
                suggestions=filtered_response.get("suggestions"),
                validation_criteria=filtered_response.get("validation_criteria"),
                metadata={
                    "original_content": {
                        "metadata": board_content.metadata,
                        "context": board_content.additional_context
                    },
                    "processed_results": len(ranked_results),
                    "final_results": len(filtered_response["search_results"])
                },
                confidence=self._calculate_confidence(filtered_response["search_results"])
            )
            
            return response

        except Exception as e:
            raise Exception(f"Error procesando contenido: {str(e)}")

    async def validate_content(
        self,
        board_content: BoardSection,
    ) -> Dict[str, Any]:
        """
        Valida el contenido proporcionado
        """
        response = await self.process_content(board_content)
        
        # Solo procesar si es tipo validación
        if response.response_type != ResponseType.VALIDATION:
            return {"valid": True}
            
        validation_result = {
            "valid": True,
            "criteria": {}
        }
        
        if response.validation_criteria:
            for criterion, description in response.validation_criteria.items():
                is_valid = any(
                    self._check_criterion(result["text"], criterion)
                    for result in response.search_results
                )
                validation_result["criteria"][criterion] = {
                    "valid": is_valid,
                    "description": description
                }
                if not is_valid:
                    validation_result["valid"] = False
                    
        return validation_result

    async def get_suggestions(
        self,
        board_content: BoardSection,
    ) -> Dict[str, Any]:
        """
        Obtiene sugerencias para el contenido proporcionado
        """
        response = await self.process_content(board_content)
        
        if response.response_type != ResponseType.SUGGESTION:
            return {"suggestions": []}
            
        return {
            "suggestions": response.suggestions or [],
            "context": [
                {
                    "text": result["text"],
                    "score": result["score"]
                }
                for result in response.search_results[:3]
            ]
        }

    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """
        Calcula el nivel de confianza basado en los scores
        """
        if not results:
            return 0.0
            
        # Promedio ponderado de los scores
        total_score = sum(result["score"] for result in results)
        return total_score / len(results)

    def _check_criterion(self, text: str, criterion: str) -> bool:
        """
        Verifica si un texto cumple con un criterio específico
        """
        criterion_checks = {
            "specific": lambda t: len(t.split()) >= 5 and any(char in t for char in "123456789"),
            "measurable": lambda t: any(word in t.lower() for word in ["medir", "medible", "métrica", "porcentaje", "cantidad"]),
            "timebound": lambda t: any(word in t.lower() for word in ["plazo", "fecha", "días", "semanas", "meses"]),
            "achievable": lambda t: not any(word in t.lower() for word in ["imposible", "irrealizable", "inalcanzable"]),
            "relevant": lambda t: len(t.split()) >= 10
        }
        
        check_func = criterion_checks.get(criterion, lambda t: True)
        return check_func(text)