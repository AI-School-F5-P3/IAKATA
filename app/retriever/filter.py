from typing import List, Dict, Any
from app.retriever.types import FilterConfig
from app.llm.types import ResponseType
from typing import Dict, List, Optional, Any

class FilterSystem:
    """Sistema de filtrado de resultados"""
    
    def __init__(self, config: FilterConfig = FilterConfig()):
        self.config = config
        
        # Mapeo de tipos de sección a tipos de respuesta
        self.category_response_types = {
            "challenge": ResponseType.VALIDATION,
            "target": ResponseType.VALIDATION,
            "obstacle": ResponseType.SUGGESTION,
            "experiment": ResponseType.VALIDATION,
            "hypothesis": ResponseType.VALIDATION,
            "process": ResponseType.SUGGESTION,
            "results": ResponseType.VALIDATION,
            "learnings": ResponseType.VALIDATION,
            "mental_contrast": ResponseType.SUGGESTION,
            "task": ResponseType.VALIDATION,
            "tribe": ResponseType.SUGGESTION
        }

        # Mapeo de tipos a tipos de respuesta
        self.type_response_types = {
            "main_content": ResponseType.CHAT,
            "example": ResponseType.SUGGESTION,
            "procedure": ResponseType.VALIDATION
        }

        # Criterios de validación por tipo
        self.validation_criteria = {
            "base": {
                "specific": "Debe ser específico y claro",
                "measurable": "Debe ser medible o verificable",
                "relevant": "Debe ser relevante para el proceso"
            },
            "target": {
                "timebound": "Debe tener un plazo definido",
                "achievable": "Debe ser alcanzable"
            },
            "experiment": {
                "testable": "Debe ser comprobable",
                "quick": "Debe ser rápido de implementar"
            },
            "hypothesis": {
                "predictive": "Debe incluir una predicción clara",
                "testable": "Debe ser verificable"
            }
        }

    def filter_results(
        self, 
        results: List[Dict[str, Any]],
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Filtra y procesa los resultados según el tipo de sección
        """
        # Aplicar filtros básicos
        filtered = self._apply_basic_filters(results)
        filtered = filtered[:self.config.max_results]
        
        # Determinar tipo de respuesta
        response_type = self._get_response_type(metadata)
        
        # Procesar según tipo
        response = {
            "search_results": filtered,
            "response_type": response_type
        }
        
        # Añadir elementos específicos según tipo
        if response_type == ResponseType.SUGGESTION:
            response["suggestions"] = self._extract_suggestions(filtered)
        elif response_type == ResponseType.VALIDATION:
            response["validation_criteria"] = self._get_validation_criteria(
                metadata.get("category") if metadata else None
            )
            
        return response

    def _apply_basic_filters(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Aplica filtros básicos a los resultados
        """
        filtered = []
        
        for result in results:
            if result['score'] < self.config.min_score:
                continue
                
            # Verificar metadata requerida
            if self.config.required_metadata:
                if not all(key in result.get('metadata', {}) 
                          for key in self.config.required_metadata):
                    continue
            
            filtered.append(result)
            
        return filtered

    def _get_response_type(self, metadata: Optional[Dict[str, str]]) -> ResponseType:
        """Determina tipo de respuesta basado en category y type"""
        if not metadata:
            return ResponseType.VALIDATION
            
        # Primero intentar por category
        if "category" in metadata:
            response_type = self.category_response_types.get(metadata["category"])
            if response_type:
                return response_type
                
        # Luego por type
        if "type" in metadata:
            response_type = self.type_response_types.get(metadata["type"])
            if response_type:
                return response_type
                
        return ResponseType.VALIDATION

    def _extract_suggestions(
        self,
        results: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extrae sugerencias de los resultados
        """
        suggestions = []
        
        for result in results:
            text = result['text']
            
            # Extraer frases que parecen sugerencias
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(start in sentence.lower() for start in [
                    "considera", "podrías", "deberías", "es recomendable",
                    "se sugiere", "intenta", "procura", "asegúrate"
                ]):
                    if sentence not in suggestions:
                        suggestions.append(sentence)
        
        return suggestions

    def _get_validation_criteria(
        self,
        section_type: str
    ) -> Dict[str, str]:
        """
        Obtiene criterios de validación para el tipo de sección
        """
        criteria = self.validation_criteria["base"].copy()
        
        # Añadir criterios específicos
        if section_type in self.validation_criteria:
            criteria.update(self.validation_criteria[section_type])
            
        return criteria