from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from .text_processor import TextProcessor
from .common_types import TextType, ProcessedText, Chunk
from .vectorizer import Vectorizer
from .metadata_manager import MetadataManager
import numpy as np
import json
from tqdm import tqdm
import re

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Versión mejorada de VectorStore con soporte para chunks
    y mejoras en la gestión de relaciones entre fragmentos.
    """
    
    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 batch_size: int = 32,
                 chunk_size: int = 512,
                 chunk_overlap: int = 50):
        """
        Inicializa el vector store con soporte para chunks
        
        Args:
            model_name: Nombre del modelo de embeddings
            batch_size: Tamaño del batch para procesamiento
            chunk_size: Tamaño objetivo de chunks en tokens
            chunk_overlap: Solapamiento entre chunks en tokens
        """
        try:
            self.text_processor = TextProcessor(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            self.vectorizer = Vectorizer(model_name=model_name)
            self.metadata_manager = MetadataManager()
            self.batch_size = batch_size
            
            # Nuevas estructuras para chunks
            self.chunk_relations = {}  # Mapeo de relaciones entre chunks
            self.section_chunks = {}   # Mapeo de secciones a chunks
            
            # Inicializar estadísticas
            self._initialize_stats()
            
            logger.info(
                f"VectorStore inicializado - Modelo: {model_name}, "
                f"Batch size: {batch_size}, Chunk size: {chunk_size}"
            )
            
        except Exception as e:
            logger.error(f"Error inicializando VectorStore: {str(e)}")
            raise

    def _initialize_stats(self):
        """Inicializa estadísticas de procesamiento"""
        self.stats = {
            'total_processed': 0,
            'successful_texts': 0,
            'failed_texts': 0,
            'total_batches': 0,
            'total_chunks': 0,
            'total_vectores': 0,
            'dimension_vectores': self.vectorizer.dimension if hasattr(self.vectorizer, 'dimension') else 0,
            'batch_size': self.batch_size,
            'tasa_exito': 0.0,
            'chunks_stats': {
                'total_chunks': 0,
                'chunks_por_seccion': {},
                'promedio_tokens_por_chunk': 0
            }
        }


    def _register_chunk_relations(self, processed_texts: List[ProcessedText]) -> None:
        """
        Registra las relaciones entre chunks para su posterior uso
        """
        try:
            for text in processed_texts:
                chunk_info = text.metadata.get('chunk_info', {})
                if not chunk_info:
                    continue
                    
                chunk_id = chunk_info['chunk_id']
                
                # Registrar en chunk_relations
                self.chunk_relations[chunk_id] = {
                    'prev_chunk': None,
                    'next_chunk': None,
                    'overlap_prev': chunk_info.get('overlap_prev'),
                    'overlap_next': chunk_info.get('overlap_next'),
                    'section_id': text.section_id
                }
                
                # Registrar en section_chunks
                if text.section_id not in self.section_chunks:
                    self.section_chunks[text.section_id] = []
                self.section_chunks[text.section_id].append(chunk_id)
                
        except Exception as e:
            logger.error(f"Error registrando relaciones de chunks: {str(e)}")

    def _process_batch(self, batch: Dict[str, List]) -> None:
        """
        Procesa un batch de chunks
        """
        try:
            if not batch['texts']:
                return
                
            # Vectorizar textos
            embeddings = self.vectorizer.add_texts(
                texts=batch['texts'],
                ids=batch['ids']
            )
            
            if embeddings is not None:
                self.stats['successful_texts'] += len(batch['texts'])
                self.stats['total_batches'] += 1
                
                # Procesar metadata
                for text, id_, meta in zip(batch['texts'], batch['ids'], batch['metadata']):
                    try:
                        chunk_info = meta.get('chunk_info', {})
                        
                        # Determinar tipo de texto
                        text_type = meta.get('text_type', TextType.MAIN_CONTENT.value)
                        
                        # Crear ProcessedText con información de chunk
                        processed_text = ProcessedText(
                            text=text,
                            text_type=TextType(text_type),
                            metadata=meta,
                            section_id=chunk_info.get('section_id', meta.get('section_id'))
                        )
                        
                        # Guardar metadata con el ID exacto
                        self.metadata_manager.save_with_id(id_, processed_text)
                        
                    except Exception as e:
                        logger.error(f"Error procesando chunk con ID {id_}: {e}")
                        
            else:
                self.stats['failed_texts'] += len(batch['texts'])
                logger.warning(f"Fallo en procesamiento de batch de {len(batch['texts'])} chunks")
                    
        except Exception as e:
            logger.error(f"Error procesando batch: {str(e)}")
            self.stats['failed_texts'] += len(batch['texts'])
            raise

    def _get_chunk_context(self, chunk_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene el contexto de un chunk incluyendo chunks relacionados
        """
        try:
            chunk_info = metadata.get('chunk_info', {})
            section_id = chunk_info.get('section_id')
            
            context = {
                'section_chunks': self.section_chunks.get(section_id, []),
                'relations': self.chunk_relations.get(chunk_id, {}),
                'position': None
            }
            
            # Determinar posición en la sección
            if section_id in self.section_chunks:
                try:
                    position = self.section_chunks[section_id].index(chunk_id)
                    total_chunks = len(self.section_chunks[section_id])
                    context['position'] = {
                        'index': position,
                        'total': total_chunks,
                        'is_first': position == 0,
                        'is_last': position == total_chunks - 1
                    }
                except ValueError:
                    pass
                    
            return context
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto de chunk: {e}")
            return {}

        
    def save(self, directory: Path) -> None:
        """
        Guarda el estado completo incluyendo información de chunks
        """
        try:
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
            
            # Guardar componentes base
            self.vectorizer.save(directory)
            self.metadata_manager.save(directory)
            
            # Guardar información de chunks
            chunk_data = {
                'relations': self.chunk_relations,
                'section_mappings': self.section_chunks
            }
            
            with open(directory / "chunk_data.json", 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"VectorStore guardado con información de chunks en {directory}")
            
        except Exception as e:
            logger.error(f"Error guardando VectorStore: {str(e)}")
            raise
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas completas del procesamiento
        Returns:
            Dict con estadísticas agregadas
        """
        try:
            vectorizer_stats = self.vectorizer.get_stats()
            metadata_stats = self.metadata_manager.get_stats()
            
            # Actualizar estadísticas de chunks
            self.stats['chunks_stats']['total_chunks'] = len(self.chunk_relations)
            for section_id, chunks in self.section_chunks.items():
                self.stats['chunks_stats']['chunks_por_seccion'][section_id] = len(chunks)
            
            # Combinar todas las estadísticas
            return {
                'total_vectores': vectorizer_stats['total_vectores'],
                'dimension_vectores': vectorizer_stats['dimension_vectores'],
                'total_batches': self.stats['total_batches'],
                'batch_size': self.batch_size,
                'textos_exitosos': self.stats['successful_texts'],
                'textos_fallidos': self.stats['failed_texts'],
                'tasa_exito': (self.stats['successful_texts'] / 
                            (self.stats['successful_texts'] + self.stats['failed_texts']) * 100
                            if (self.stats['successful_texts'] + self.stats['failed_texts']) > 0
                            else 0),
                'chunks_stats': self.stats['chunks_stats'],
                'metadata_stats': metadata_stats
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}

    def load(self, directory: Path) -> None:
        """
        Carga el estado completo incluyendo información de chunks
        """
        try:
            # Cargar componentes base
            self.vectorizer.load(directory)
            self.metadata_manager.load(directory)
            
            # Cargar información de chunks
            chunk_data_file = directory / "chunk_data.json"
            if chunk_data_file.exists():
                with open(chunk_data_file, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                    self.chunk_relations = chunk_data['relations']
                    self.section_chunks = chunk_data['section_mappings']
            # Añadir logs de debug aquí
            logger.info(f"Número de vectores en el índice FAISS: {self.vectorizer.index.ntotal}")
            logger.info(f"Número de text_ids: {len(self.vectorizer.text_ids)}")
            logger.info(f"Número de entradas en metadata: {len(self.metadata_manager.metadata)}")        
            logger.info(f"VectorStore cargado con información de chunks desde {directory}")
            
        except Exception as e:
            logger.error(f"Error cargando VectorStore: {str(e)}")
            raise