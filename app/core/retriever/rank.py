from typing import List, Dict, Any
from core.retriever.types import SearchResult, RankingConfig

class RankEngine:
    """Motor de ranking de resultados"""
    
    def __init__(self, config: RankingConfig = RankingConfig()):
        self.config = config
        
        # Factores de boost por tipo de contenido
        self.type_boosts = {
            "challenge": {
                "keywords": ["objetivo", "meta", "reto"],
                "boost": 1.1  # Reducir el boost para evitar que todos alcancen el máximo
            },
            "target": {
                "keywords": ["estado objetivo", "meta intermedia"],
                "boost": 1.1
            },
            "experiment": {
                "keywords": ["experimento", "hipótesis", "prueba"],
                "boost": 1.1
            },
            "hypothesis": {
                "keywords": ["hipótesis", "predicción", "resultado esperado"],
                "boost": 1.1
            }
        }

    def rank_results(
        self,
        results: List[SearchResult],
        metadata: Dict[str, str],
        keywords: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Rankea y ajusta scores de los resultados basándose en la categoría y palabras clave.
        """
        ranked_results = []

        # Si no se proporciona metadata, inicializarla como un diccionario vacío
        if metadata is None:
            metadata = {}

        # Si no se proporcionan keywords, inicializarlas como una lista vacía
        if keywords is None:
            keywords = []

        # Obtener la categoría de la metadata (o usar "general" por defecto)
        category = metadata.get("category", "general")
        print(f"Resultados recibidos: {results}")

        for result in results:
            # Calcular score ajustado usando la categoría
            adjusted_score = self._calculate_adjusted_score(
                result.score,
                result.text,
                category,  # Usar la categoría extraída
                keywords
            )

            print(f"Adjusted score: {adjusted_score}, Threshold: {self.config.base_threshold}")
            
            # Filtrar resultados que superen el umbral
            if adjusted_score >= self.config.base_threshold:
                ranked_results.append({
                    "id": result.id,
                    "text": result.text,
                    "score": adjusted_score,
                    "metadata": result.metadata
                })
                 
        # Ordenar por score ajustado de mayor a menor
        ranked_results = sorted(ranked_results, key=lambda x: x['score'], reverse=True)
        print("Resultados rankeados:", ranked_results)
        return ranked_results

    def _calculate_adjusted_score(
        self,
        base_score: float,
        text: str,
        category: str,  # Renombrado: se espera el string de la categoría
        keywords: List[str]
    ) -> float:
        """
        Calcula score ajustado basado en múltiples factores
        """
        adjusted_score = base_score
        
        # 1. Ajuste por keywords relevantes
        keyword_matches = sum(1 for keyword in keywords 
                              if keyword.lower() in text.lower())
        adjusted_score += (keyword_matches * self.config.keyword_boost)
        
        # 2. Ajuste por tipo de contenido (usando la categoría)
        type_boost = self.type_boosts.get(category)
        if type_boost:
            if any(kw.lower() in text.lower() for kw in type_boost["keywords"]):
                adjusted_score *= type_boost["boost"]
        
        # 3. Ajuste por calidad de contenido
        # Bonus por contener elementos estructurales
        if any(marker in text for marker in ["1.", "2.", "•", "-", ":"]):
            adjusted_score *= 1.05  # Reducir el boost para evitar que todos alcancen el máximo
             
        # Asegurar que el score final está en el rango [0, self.config.max_score]
        return min(max(adjusted_score, 0.0), self.config.max_score)