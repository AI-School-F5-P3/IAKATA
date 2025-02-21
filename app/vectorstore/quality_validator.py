from typing import Optional, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)

class QualityValidator:
    """
    Valida la calidad de embeddings y resultados
    """
    @staticmethod
    def validate_embedding(embedding: Optional[np.ndarray]) -> bool:
        """
        Valida la calidad de un embedding
        Args:
            embedding: Array numpy del embedding
        Returns:
            bool indicando si el embedding es válido
        """
        if embedding is None:
            return False
            
        try:
            # Verificar dimensiones
            if len(embedding.shape) != 2:
                return False
                
            # Verificar valores numéricos válidos
            if not np.all(np.isfinite(embedding)):
                return False
                
            # Verificar norma del vector
            norm = np.linalg.norm(embedding)
            if not (0.1 <= norm <= 10.0):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error en validación de embedding: {e}")
            return False
    
    @staticmethod
    def validate_search_result(result: Dict[str, Any]) -> bool:
        """
        Valida la calidad de un resultado de búsqueda
        Args:
            result: Diccionario con el resultado
        Returns:
            bool indicando si el resultado es válido
        """
        try:
            required_fields = ['id', 'score', 'text']
            if not all(field in result for field in required_fields):
                return False
                
            # Validar score
            if not (0 <= result['score'] <= 1):
                return False
                
            # Validar texto
            if not isinstance(result['text'], str) or not result['text'].strip():
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error en validación de resultado: {e}")
            return False
        
    def validate_section(self, section: Dict) -> bool:
        """
        Valida que una sección tenga todos los campos requeridos y sean válidos
        """
        required_fields = {
            'title': str,
            'page_range': list,
            'primary_category': str,
            'secondary_categories': list,
            'relevance': dict,
            'key_concepts': dict
        }
        
        try:
            # Validar campos requeridos y tipos
            for field, field_type in required_fields.items():
                if field not in section:
                    self.logger.warning(f"Campo requerido faltante: {field}")
                    return False
                if not isinstance(section[field], field_type):
                    self.logger.warning(f"Tipo inválido para {field}: {type(section[field])}")
                    return False
                    
            # Validar estructura de relevance
            if not all(k in section['relevance'] for k in ['level', 'score']):
                self.logger.warning("Estructura de relevance incompleta")
                return False
                
            # Validar estructura de key_concepts
            required_concept_types = ['methodologies', 'practices', 'tools', 'roles']
            if not all(k in section['key_concepts'] for k in required_concept_types):
                self.logger.warning("Estructura de key_concepts incompleta")
                return False
            
            # Validación más flexible para secciones críticas
            if self.is_critical_section(section):
                # Si es una sección crítica pero no tiene conceptos, los añadimos
                if 'key_concepts' not in section:
                    section['key_concepts'] = {}
                if 'methodologies' not in section['key_concepts']:
                    section['key_concepts']['methodologies'] = []
                
                # Asegurar que tenga al menos un concepto Kata
                if not any(concept in section['key_concepts']['methodologies'] 
                        for concept in ['Kata de mejora', 'Coaching Kata']):
                    section['key_concepts']['methodologies'].append('Kata de mejora')
                    self.logger.info(f"Añadido concepto Kata a sección crítica: {section['title']}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error en validación de sección: {str(e)}")
            return False