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

    def _process_section(self, section: Dict[str, Any], book_filename: str) -> List[ProcessedText]:
        """
        Procesa una sección y retorna textos procesados con chunks
        """
        try:
            if not isinstance(section, dict):
                logger.error(f"Sección inválida: {section}")
                return []
                
            # Asegurar que metadata existe
            section['metadata'] = section.get('metadata', {})
            section['metadata']['book_filename'] = book_filename
            
            # Procesar sección usando el TextProcessor con chunking
            processed_texts = self.text_processor.process_section(section)
            
            # Registrar relaciones entre chunks
            self._register_chunk_relations(processed_texts)
            
            return processed_texts
                        
        except Exception as e:
            logger.error(f"Error procesando sección: {str(e)}")
            return []

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
        
    def process_and_index(self, structure_file: Path) -> Dict[str, Any]:
        """
        Procesa y vectoriza el archivo de análisis estructural
        
        Args:
            structure_file: Ruta al archivo JSON de análisis estructural
        Returns:
            Dict con estadísticas del procesamiento
        """
        try:
            # Validar y cargar archivo
            structure_file = Path(structure_file)
            if not structure_file.exists():
                raise FileNotFoundError(f"No se encontró el archivo: {structure_file}")
                
            with open(structure_file, 'r', encoding='utf-8') as f:
                structure = json.load(f)
            
            if 'books_analysis' not in structure:
                raise ValueError("El archivo JSON no tiene la estructura esperada")
            
            # Inicializar procesamiento por batches
            current_batch = {
                'texts': [],
                'ids': [],
                'metadata': []
            }
            
            # Calcular total de secciones
            total_sections = sum(
                len(book['analysis'].get('relevant_sections', []))
                for book in structure['books_analysis']
            )
            
            # Procesar libros
            with tqdm(total=total_sections, desc="Procesando secciones") as pbar:
                for book in structure['books_analysis']:
                    logger.info(f"Procesando libro: {book['filename']}")
                    
                    for section in book['analysis'].get('relevant_sections', []):
                        if not isinstance(section, dict):
                            logger.warning(f"Sección inválida en {book['filename']}")
                            continue
                            
                        processed_texts = self._process_section(section, book['filename'])
                        
                        for processed_text in processed_texts:
                            if not processed_text.text.strip():
                                continue
                                
                            text_id = self.metadata_manager.generate_id(processed_text)
                            current_batch['texts'].append(processed_text.text)
                            current_batch['ids'].append(text_id)
                            current_batch['metadata'].append(processed_text.metadata)
                            
                            if len(current_batch['texts']) >= self.batch_size:
                                self._process_batch(current_batch)
                                current_batch = {'texts': [], 'ids': [], 'metadata': []}
                                
                        pbar.update(1)
                
                # Procesar último batch si existe
                if current_batch['texts']:
                    self._process_batch(current_batch)
                    
            return self.get_stats()
            
        except Exception as e:
            logger.error(f"Error en process_and_index: {str(e)}")
            raise
    
    
    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda híbrida con consciencia de chunks
        """
        try:
            logger.info(f"Iniciando búsqueda híbrida para query: {query}")
            logger.info(f"Número de vectores en el índice FAISS: {self.vectorizer.index.ntotal}")
            logger.info(f"Número de text_ids: {len(self.vectorizer.text_ids)}")
            logger.info(f"Número de entradas en metadata: {len(self.metadata_manager.metadata)}")
            
            # Vectorizar query
            
            query_embedding = self.vectorizer.vectorize([query])
            if query_embedding is None:
                raise ValueError("No se pudo vectorizar la consulta")
                
            # Búsqueda semántica
            scores, indices = self.vectorizer.search(
                query_embedding,
                k=top_k * 3  # Buscar más resultados para post-procesamiento
            )
            
            # Asegurar que scores e indices son arrays 2D
            if len(scores.shape) == 1:
                scores = scores.reshape(1, -1)
            if len(indices.shape) == 1:
                indices = indices.reshape(1, -1)
            
            # Preparar resultados
            results = []
            seen_texts = set()
            
            # Iterar sobre los resultados de la primera fila
            for idx, score in zip(indices[0], scores[0]):
                # Convertir a índice Python int
                idx = int(idx)
                score = float(score)
                
                # Verificar que el índice es válido
                if idx >= len(self.vectorizer.text_ids):
                    logger.warning(f"Índice {idx} fuera de rango")
                    continue
                    
                # Obtener el ID del texto
                text_id = self.vectorizer.text_ids[idx]
                
                # Obtener metadata
                metadata = self.metadata_manager.get_entry(text_id)
                if metadata is None:
                    continue
                    
                # Obtener contexto del chunk
                context = self._get_chunk_context(text_id, metadata)
                
                # Calcular score final
                final_score = self._calculate_final_score(
                    semantic_score=score,
                    metadata=metadata,
                    query=query,
                    context=context
                )
                
                # Usar umbral más bajo (0.2) para ser menos restrictivo
                if final_score > 0.2:
                    text = metadata.get('text', '')
                    text_hash = hash(text)
                    
                    if text_hash not in seen_texts:
                        # Asegurar que el resultado tenga todos los campos necesarios
                        result = {
                            'id': text_id,
                            'text': text,
                            'score': final_score,
                            'type': metadata.get('type', ''),
                            'metadata': metadata,
                            'context': context
                        }
                        results.append(result)
                        seen_texts.add(text_hash)
            
            # Ordenar por score final y tomar los top_k
            results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
            
            logger.info(f"Búsqueda completada con {len(results)} resultados relevantes")
            return results
                
        except Exception as e:
            logger.error(f"Error en búsqueda híbrida: {e}")
            return []


    
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

    def _calculate_final_score(
        self,
        semantic_score: float,
        metadata: Dict[str, Any],
        query: str,
        context: Dict[str, Any]
    ) -> float:
        """
        Calcula score final considerando metadata y contexto de chunks
        """
        try:
            base_score = semantic_score * 0.5
            text = metadata.get('text', '').lower()
            query_lower = query.lower()

            # Early returns y penalizaciones fuertes
            irrelevant_terms = [
                'copyright', 'isbn', 'reproducción', 'distribución', 'reservados',
                'todos los derechos', 'editorial', 'impreso en'
            ]
            if any(term in text for term in irrelevant_terms):
                return base_score * 0.2

            if 'introducción' in text and not any(term in text for term in ['implementar', 'método', 'paso']):
                base_score *= 0.6

            # 1. Evaluar relevancia directa a la query
            multiplier = 1.0

            # Detección de conceptos Lean Kata
            lean_kata_concepts = [
                'kata de mejora', 'kata de coaching', 'lean kata',
                'estado actual', 'estado objetivo', 'condición objetivo'
            ]
            if any(concept in text for concept in lean_kata_concepts):
                multiplier *= 1.1

            if 'cómo' in query_lower:
                # Penalizar referencias indirectas
                if 'coaching kata' in text and not any(term in text for term in ['implementar', 'paso', 'método']):
                    multiplier *= 0.7
                # Boost para contenido práctico
                practical_terms = [
                    'implementar', 'aplicar', 'paso', 'método',
                    'procedimiento', 'realizar', 'ejecutar', 'llevar a cabo'
                ]
                if any(term in text for term in practical_terms):
                    multiplier *= 1.4
            elif 'qué' in query_lower:
                if any(term in text for term in ['es', 'significa', 'definición', 'concepto']):
                    multiplier *= 1.3
                if 'lean kata' in text:
                    multiplier *= 1.2
            elif 'por qué' in query_lower:
                if any(term in text for term in ['beneficio', 'ventaja', 'mejora', 'resultado']):
                    multiplier *= 1.3
            elif 'cuál' in query_lower or 'cuáles' in query_lower:
                if any(term in text for term in ['paso', 'etapa', 'fase']):
                    multiplier *= 1.4
                if '1.' in text or 'primero' in text:
                    multiplier *= 1.2

            # 2. Evaluar estructura del contenido
            content_type = metadata.get('type', '')
            if content_type == 'procedure':
                sequence_markers = [
                    str(i) + '.' for i in range(1, 6)
                ] + ['primero', 'segundo', 'tercero', 'siguiente', 'después', 'luego']
                if any(marker in text for marker in sequence_markers):
                    multiplier *= 1.3
            elif content_type == 'example':
                if 'cómo' in query_lower and any(term in text for term in ['implementar', 'aplicar']):
                    multiplier *= 1.1

            # 3. Ajuste por longitud
            text_length = len(text)
            if text_length < 100:
                multiplier *= 0.7
            elif text_length < 200:
                multiplier *= 0.8

            # 4. Calcular score final
            final_score = base_score * min(multiplier, 1.5)

            # 5. Límites según tipo de contenido y query
            if 'cómo' in query_lower or 'cuál' in query_lower:
                max_score = 0.75 if content_type == 'procedure' else 0.6
            else:
                max_score = 0.65 if content_type == 'main_content' else 0.7

            return min(max(final_score, 0.0), max_score)

        except Exception as e:
            logger.error(f"Error calculando score final: {e}")
            return semantic_score * 0.3
        
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