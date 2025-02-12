# Mejora de la clase Vectorizer
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path
import torch
from cache_manager import CacheManager
from quality_validator import QualityValidator
from retry_manager import RetryManager

logger = logging.getLogger(__name__)

class Vectorizer:
    """
    Versión mejorada del Vectorizer que maneja la generación de embeddings y gestión del índice FAISS
    Incluye mejor manejo de errores y validación de datos
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', device: str = None):
        """
        Inicializa el vectorizador con opciones mejoradas
        Args:
            model_name: Nombre del modelo de sentence-transformers
            device: Dispositivo para procesamiento ('cpu' o 'cuda')
        """
        try:
            # Configurar dispositivo
            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Utilizando dispositivo: {self.device}")
            
            # Inicializar modelo
            self.model = SentenceTransformer(model_name, device=self.device)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.cache_manager = CacheManager(cache_dir=Path("./cache/embeddings"))
            self.quality_validator = QualityValidator()

            
            # Inicializar índice FAISS
            self.index = faiss.IndexFlatIP(self.dimension)
            if self.device == 'cuda' and faiss.get_num_gpus() > 0:
                self.index = faiss.index_cpu_to_gpu(
                    faiss.StandardGpuResources(),
                    0,
                    self.index
                )
            
            # Estructuras de datos para tracking
            self.text_ids = []
            self.metadata = {}
            self._initialize_stats()
            
            logger.info(f"Vectorizer inicializado - Dimensión: {self.dimension}")
            
        except Exception as e:
            logger.error(f"Error en inicialización del Vectorizer: {str(e)}")
            raise

    def _initialize_stats(self):
        """Inicializa estadísticas de procesamiento"""
        self.stats = {
            'total_processed': 0,
            'successful_embeddings': 0,
            'failed_embeddings': 0,
            'total_batches': 0,
            'average_embedding_time': 0
        }

    def _validate_texts(self, texts: List[str]) -> List[str]:
        """
        Valida y preprocesa los textos antes de la vectorización
        Args:
            texts: Lista de textos a validar
        Returns:
            Lista de textos válidos
        """
        valid_texts = []
        for text in texts:
            if not isinstance(text, str):
                logger.warning(f"Texto inválido encontrado: {type(text)}")
                continue
            if not text.strip():
                logger.warning("Texto vacío encontrado")
                continue
            valid_texts.append(text.strip())
        return valid_texts

    @RetryManager.with_retry()
    def vectorize(self, texts: List[str], batch_size: int = 32) -> Optional[np.ndarray]:
        """
        Genera embeddings para una lista de textos con mejor manejo de errores y caché
        Args:
            texts: Lista de textos a vectorizar
            batch_size: Tamaño del batch para procesamiento
        Returns:
            Array numpy con los embeddings o None si hay error
        """
        try:
            # Validar textos
            valid_texts = self._validate_texts(texts)
            if not valid_texts:
                logger.error("No hay textos válidos para vectorizar")
                return None

            # Si es un solo texto, intentar recuperar de caché
            if len(valid_texts) == 1:
                text_hash = self.cache_manager.get_text_hash(valid_texts[0])
                cached_embedding = self.cache_manager.get_cached_embedding(text_hash)
                if cached_embedding is not None:
                    logger.debug("Embedding recuperado de caché")
                    return cached_embedding

            # Procesar en batches para mejor manejo de memoria
            all_embeddings = []
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i:i + batch_size]
                
                # Generar embeddings del batch
                with torch.no_grad():
                    embeddings = self.model.encode(
                        batch,
                        convert_to_numpy=True,
                        show_progress_bar=False,
                        batch_size=batch_size
                    )
                    
                if not isinstance(embeddings, np.ndarray):
                    raise ValueError(f"Embeddings inválidos generados: {type(embeddings)}")
                    
                # Validar calidad del batch
                if not self.quality_validator.validate_embedding(embeddings):
                    raise ValueError(f"Embeddings del batch no cumplen criterios de calidad")
                    
                all_embeddings.append(embeddings)

            # Concatenar todos los embeddings
            final_embeddings = np.vstack(all_embeddings)
            
            # Normalizar para similitud por coseno
            faiss.normalize_L2(final_embeddings)
            
            # Actualizar estadísticas
            self.stats['successful_embeddings'] += len(valid_texts)
            
            # Si era un solo texto, guardar en caché
            if len(valid_texts) == 1:
                self.cache_manager.cache_embedding(valid_texts[0], final_embeddings)
                
            return final_embeddings
            
        except Exception as e:
            logger.error(f"Error en vectorización: {str(e)}")
            self.stats['failed_embeddings'] += len(texts)
            return None

    def add_texts(self, texts: List[str], ids: List[str], 
                 metadata: Optional[List[Dict[str, Any]]] = None) -> np.ndarray:
        """
        Añade textos al índice con metadata asociada
        Args:
            texts: Lista de textos a añadir
            ids: Lista de identificadores correspondientes
            metadata: Lista opcional de metadatos por texto
        Returns:
            Array numpy con los embeddings generados
        """
        try:
            if len(texts) != len(ids):
                raise ValueError("Número diferente de textos e IDs")
                
            embeddings = self.vectorize(texts)
            if embeddings is None:
                raise ValueError("Fallo en generación de embeddings")
                
            # Añadir al índice FAISS
            self.index.add(embeddings)
            
            # Almacenar IDs y metadata
            self.text_ids.extend(ids)
            if metadata:
                for id_, meta in zip(ids, metadata):
                    self.metadata[id_] = meta
                    
            return embeddings
            
        except Exception as e:
            logger.error(f"Error añadiendo textos: {str(e)}")
            raise

    # En la clase Vectorizer
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del vectorizador"""
        total = self.stats['successful_embeddings'] + self.stats['failed_embeddings']
        success_rate = (self.stats['successful_embeddings'] / total * 100) if total > 0 else 0
        
        return {
            'total_vectores': len(self.text_ids),
            'dimension_vectores': self.dimension,  # Cambiado de 'dimension'
            'textos_exitosos': self.stats['successful_embeddings'],
            'textos_fallidos': self.stats['failed_embeddings'],
            'tasa_exito': success_rate,
            'total_batches': self.stats['total_batches']
        }

    def save(self, directory: Path):
        """
        Guarda el estado completo del vectorizer
        Args:
            directory: Directorio donde guardar los archivos
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            
            # Guardar índice FAISS
            index_path = directory / "faiss.index"
            faiss.write_index(self.index, str(index_path))
                    
            # Guardar IDs y metadata
            np.save(str(directory / "text_ids.npy"), np.array(self.text_ids))
            np.save(str(directory / "metadata.npy"), self.metadata)
            
            # Guardar estadísticas
            np.save(str(directory / "stats.npy"), self.stats)
            
            logger.info(f"Vectorizer guardado en {directory}")
            
        except Exception as e:
            logger.error(f"Error guardando Vectorizer: {str(e)}")
            raise

    def load(self, directory: Path):
        """
        Carga el estado completo del vectorizador
        Args:
            directory: Directorio desde donde cargar
        """
        try:
            # Cargar índice FAISS
            index_path = directory / "faiss.index"
            self.index = faiss.read_index(str(index_path))
            
            # Mover a GPU si está disponible
            if self.device == 'cuda' and faiss.get_num_gpus() > 0:
                self.index = faiss.index_cpu_to_gpu(
                    faiss.StandardGpuResources(),
                    0,
                    self.index
                )
                
            # Cargar datos auxiliares
            self.text_ids = np.load(str(directory / "text_ids.npy")).tolist()
            self.metadata = np.load(str(directory / "metadata.npy"), allow_pickle=True).item()
            self.stats = np.load(str(directory / "stats.npy"), allow_pickle=True).item()
            
            logger.info(f"Vectorizer cargado desde {directory}")
            
        except Exception as e:
            logger.error(f"Error cargando Vectorizer: {str(e)}")
            raise
        
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[np.ndarray, List[str]]:
        """
        Busca los vectores más similares para un embedding de consulta
        """
        try:
            logger.info(f"Iniciando búsqueda en índice FAISS")
            
            # Asegurar que el query es 2D
            if len(query_embedding.shape) == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            logger.info(f"Query shape después de reshape: {query_embedding.shape}")
            
            # Normalizar vector de consulta
            faiss.normalize_L2(query_embedding)
            
            # Verificar índice
            if self.index.ntotal == 0:
                logger.error("El índice FAISS está vacío")
                return np.array([]), []
                
            logger.info(f"Índice FAISS contiene {self.index.ntotal} vectores")
            
            # Realizar búsqueda
            distances, indices = self.index.search(
                query_embedding.astype(np.float32),
                min(k, self.index.ntotal)
            )
            
            logger.info(f"Búsqueda FAISS completada - Distancias: {distances}")
            logger.info(f"Índices encontrados: {indices}")
            
            # Convertir distancias a scores
            scores = distances[0]
            
            # Obtener IDs
            result_ids = [self.text_ids[idx] for idx in indices[0] if idx < len(self.text_ids)]
            
            logger.info(f"IDs recuperados: {result_ids}")
            
            return scores, result_ids
                
        except Exception as e:
            logger.error(f"Error en búsqueda FAISS: {e}", exc_info=True)
            return np.array([]), []