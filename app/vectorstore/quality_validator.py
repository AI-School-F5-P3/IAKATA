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