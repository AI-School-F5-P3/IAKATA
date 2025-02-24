from typing import Optional, Dict, Any
import numpy as np
from functools import lru_cache
import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestiona el sistema de caché para embeddings y resultados de búsqueda
    """
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir
        if cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Caché en memoria para resultados frecuentes
        self.results_cache: Dict[str, Any] = {}
        
    @staticmethod
    def get_text_hash(text: str) -> str:
        """Genera un hash único para un texto"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    @lru_cache(maxsize=1000)
    def get_cached_embedding(self, text_hash: str) -> Optional[np.ndarray]:
        """Recupera un embedding cacheado por su hash"""
        if not self.cache_dir:
            return None
            
        cache_file = self.cache_dir / f"{text_hash}.npy"
        if cache_file.exists():
            try:
                return np.load(str(cache_file))
            except Exception as e:
                logger.error(f"Error cargando embedding cacheado: {e}")
                return None
        return None
    
    def cache_embedding(self, text: str, embedding: np.ndarray) -> None:
        """Guarda un embedding en caché"""
        if not self.cache_dir:
            return
            
        text_hash = self.get_text_hash(text)
        cache_file = self.cache_dir / f"{text_hash}.npy"
        try:
            np.save(str(cache_file), embedding)
        except Exception as e:
            logger.error(f"Error guardando embedding en caché: {e}")
    
    def cache_search_result(self, query: str, result: Dict[str, Any]) -> None:
        """Guarda un resultado de búsqueda en caché"""
        query_hash = self.get_text_hash(query)
        self.results_cache[query_hash] = {
            'result': result,
            'timestamp': import_time.time()
        }
    
    def get_cached_search_result(self, query: str) -> Optional[Dict[str, Any]]:
        """Recupera un resultado de búsqueda cacheado"""
        query_hash = self.get_text_hash(query)
        cached = self.results_cache.get(query_hash)
        if cached and (import_time.time() - cached['timestamp']) < 3600:  # 1 hora de validez
            return cached['result']
        return None