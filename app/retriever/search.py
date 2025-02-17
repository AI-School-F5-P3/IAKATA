from typing import List, Dict, Any
from app.retriever.types import SearchQuery, SearchResult
from typing import Dict, List, Optional

class SearchEngine:
    """Motor de búsqueda que interactúa con el vector store"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        
        # Keywords por tipo de sección para enriquecer queries
        self.category_keywords = {
            "challenge": ["reto", "desafío", "objetivo estratégico", "meta global"],
            "target": ["estado objetivo", "meta intermedia", "condición deseada"],
            "obstacle": ["obstáculo", "impedimento", "barrera", "dificultad"],
            "experiment": ["experimento", "prueba", "ensayo", "kata de mejora"],
            "hypothesis": ["hipótesis", "predicción", "teoría", "resultado esperado"],
            "process": ["proceso", "método", "procedimiento", "kata"],
            "results": ["resultado", "medición", "métrica", "indicador"],
            "learnings": ["aprendizaje", "lección", "insight", "conclusión"],
            "mental_contrast": ["contraste", "evaluación", "comparación"],
            "task": ["tarea", "actividad", "paso", "acción"],
            "tribe": ["equipo", "grupo", "roles", "responsabilidades"]
        }

    async def search(self, query: SearchQuery) -> List[SearchResult]:
        if not query:
            raise ValueError("Query cannot be empty")
    
        """
        Realiza la búsqueda en el vector store
        """
        try:
            # Enriquecer query con keywords relevantes
            enriched_query = self._enrich_query(query.text, query.metadata)
            
            # Buscar en vector store
            results = self.vector_store.hybrid_search(
                query=enriched_query,
                top_k=query.max_results * 2  # Buscar más para filtrar después
            )
            print(results)
            # Convertir a SearchResults
            return [
                SearchResult(
                    id=result['id'],
                    text=result['text'],
                    score=result['score'],
                    metadata=result['metadata']
                ) for result in results
            ]

        except Exception as e:
            raise Exception(f"Error en búsqueda: {str(e)}")

    def _enrich_query(self, content: str, category: Optional[str] = None) -> str:
        """
        Enriquecer la consulta agregando información de la categoría.
        Si se proporciona una categoría, se añade una línea con "Relacionado con: <category>".
        """
        if category:
            return f"{content}\nRelacionado con: {category}"
        return content

    def get_section_keywords(self, section_type: dict) -> List[str]:
        """
        Retorna keywords asociadas a un tipo de sección
        """
        section = section_type["category"]
        return self.category_keywords.get(section, [])