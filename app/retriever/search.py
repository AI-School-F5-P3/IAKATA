from typing import List, Dict, Any
from app.retriever.types import SearchQuery, SearchResult
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SearchEngine:
    """Motor de búsqueda que interactúa con el vector store"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.vectorizer = vector_store.vectorizer  # Obtener el vectorizer del vector_store
        self.text_ids = vector_store.vectorizer.text_ids     # Obtener los text_ids del vector_store
        self.metadata_manager = vector_store.metadata_manager  # Obtener el metadata_manager
        self.section_chunks = vector_store.section_chunks  
        self.chunk_relations = vector_store.chunk_relations
        
        logger.info("SearchEngine inicializado con vectorizer y metadata")

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
            scores, indices = self.vector_store.vectorizer.search(
                query_embedding, k=top_k * 3
                )

            logger.info(f"Búsqueda completada - scores: {len(scores)}, indices: {len(indices)}")
            
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