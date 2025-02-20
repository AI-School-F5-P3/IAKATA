from typing import Dict, Any, List
from app.retriever.types import (
    BoardSection,
    SearchQuery,
    RankingConfig,
    FilterConfig,
    RetrieverResponse
)
from app.retriever.search import SearchEngine
from app.retriever.rank import RankEngine
from app.retriever.filter import FilterSystem
from app.llm.types import ResponseType
from app.vectorstore.common_types import ProcessedText
from tqdm import tqdm
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class RetrieverSystem:
    """
    Sistema principal de recuperación que coordina búsqueda, 
    ranking y filtrado
    """
    
    def __init__(
        self,
        vector_store,
        ranking_config: RankingConfig = RankingConfig(),
        filter_config: FilterConfig = FilterConfig()
    ):
        self.search_engine = SearchEngine(vector_store)
        self.rank_engine = RankEngine(ranking_config)
        self.filter_system = FilterSystem(filter_config)

    async def process_content(
        self,
        board_content: BoardSection,
        max_results: int = 5
    ) -> RetrieverResponse:
        """
        Procesa contenido del tablero y retorna resultados relevantes
        """
        try:
            # 1. Preparar query
            search_query = SearchQuery(
                text=board_content.content,
                metadata=board_content.metadata,
                max_results=max_results
            )
            
            # 2. Realizar búsqueda
            search_results = await self.search_engine.search(search_query)
            
            logger.info(f"Resultados de búsqueda: {len(search_results)}")

            # 3. Obtener keywords para ranking
            keywords = self.search_engine.get_section_keywords(board_content.metadata)
            
            # 4. Rankear resultados
            ranked_results = self.rank_engine.rank_results(
                results=search_results,
                keywords=keywords,
                metadata=board_content.metadata
            )
            
            # 5. Filtrar y procesar resultados
            filtered_response = self.filter_system.filter_results(
                results=ranked_results,
                metadata=board_content.metadata
            )
            
            # 6. Construir respuesta final
            response = RetrieverResponse(
                response_type=filtered_response["response_type"],
                search_results=filtered_response["search_results"],
                suggestions=filtered_response.get("suggestions"),
                validation_criteria=filtered_response.get("validation_criteria"),
                metadata={
                    "original_content": {
                        "metadata": board_content.metadata,
                        "context": board_content.additional_context
                    },
                    "processed_results": len(ranked_results),
                    "final_results": len(filtered_response["search_results"])
                },
                confidence=self._calculate_confidence(filtered_response["search_results"])
            )
            
            return response

        except Exception as e:
            raise Exception(f"Error procesando contenido: {str(e)}")
    
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

    async def validate_content(
        self,
        board_content: BoardSection,
    ) -> Dict[str, Any]:
        """
        Valida el contenido proporcionado
        """
        response = await self.process_content(board_content)
        
        # Solo procesar si es tipo validación
        if response.response_type != ResponseType.VALIDATION:
            return {"valid": True}
            
        validation_result = {
            "valid": True,
            "criteria": {}
        }
        
        if response.validation_criteria:
            for criterion, description in response.validation_criteria.items():
                is_valid = any(
                    self._check_criterion(result["text"], criterion)
                    for result in response.search_results
                )
                validation_result["criteria"][criterion] = {
                    "valid": is_valid,
                    "description": description
                }
                if not is_valid:
                    validation_result["valid"] = False
                    
        return validation_result

    async def get_suggestions(
        self,
        board_content: BoardSection,
    ) -> Dict[str, Any]:
        """
        Obtiene sugerencias para el contenido proporcionado
        """
        response = await self.process_content(board_content)
        
        if response.response_type != ResponseType.SUGGESTION:
            return {"suggestions": []}
            
        return {
            "suggestions": response.suggestions or [],
            "context": [
                {
                    "text": result["text"],
                    "score": result["score"]
                }
                for result in response.search_results[:3]
            ]
        }

    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """
        Calcula el nivel de confianza basado en los scores
        """
        if not results:
            return 0.0
            
        # Promedio ponderado de los scores
        total_score = sum(result["score"] for result in results)
        return total_score / len(results)

    def _check_criterion(self, text: str, criterion: str) -> bool:
        """
        Verifica si un texto cumple con un criterio específico
        """
        criterion_checks = {
            "specific": lambda t: len(t.split()) >= 5 and any(char in t for char in "123456789"),
            "measurable": lambda t: any(word in t.lower() for word in ["medir", "medible", "métrica", "porcentaje", "cantidad"]),
            "timebound": lambda t: any(word in t.lower() for word in ["plazo", "fecha", "días", "semanas", "meses"]),
            "achievable": lambda t: not any(word in t.lower() for word in ["imposible", "irrealizable", "inalcanzable"]),
            "relevant": lambda t: len(t.split()) >= 10
        }
        
        check_func = criterion_checks.get(criterion, lambda t: True)
        return check_func(text)