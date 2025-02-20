from typing import Dict, List, Optional, Any, Awaitable
from pydantic import BaseModel
from datetime import datetime

from .query_classifier import QueryClassifier
from app.vectorstore.vector_store import VectorStore
from app.vectorstore.common_types import TextType, ProcessedText
from app.llm.types import LLMRequest, LLMResponse, ResponseType
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.retriever.types import SearchQuery, SearchResult
import logging

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    def __init__(
        self,
        vector_store: VectorStore,
        llm: LLMModule,
        validator: ResponseValidator
    ):
        self.vector_store = vector_store
        self.llm = llm
        self.validator = validator
        self.query_classifier = QueryClassifier()
        self.context_window = 4000

    async def process_query(
        self,
        query: str,
        response_type: ResponseType,
        top_k: int = 5,
        temperature: Optional[float] = None,
        language: str = "es",
        metadata: Optional[Dict[str, str]] = None
    ) -> LLMResponse:
        """
        Procesa una consulta determinando si usar RAG para Lean Kata o respuesta general
        """
        try:
            # Clasificar la consulta
            is_lean_kata, query_metadata = self.query_classifier.classify_query(query)
            
            # Base metadata
            base_metadata = {
                'text': query,
                'type': response_type.value,
                'metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'language': language,
                    **(metadata or {}),
                    **query_metadata['metadata']
                },
                'section_id': query_metadata['section_id']
            }

            if is_lean_kata:
                # Proceso completo RAG para consultas Lean Kata
                search_results = await self._search_relevant_docs(
                    query=query,
                    metadata=base_metadata,
                    top_k=top_k
                )
                
                context = await self._build_context(search_results)
                base_metadata['metadata'].update({
                    'search_results': len(search_results),
                    'top_score': max(r['score'] for r in search_results) if search_results else 0
                })
            else:
                # Para consultas generales, no necesitamos búsqueda
                search_results = []
                context = {
                    'query_type': 'general',
                    'metadata': base_metadata
                }

            # Preparar solicitud al LLM
            llm_request = LLMRequest(
                query=query,
                context=context,
                response_type=response_type,
                temperature=temperature,
                language=language
            )
            
            # Obtener respuesta
            llm_response = await self.llm.process_request(llm_request)
            
            if is_lean_kata:
                # Solo validar y enriquecer respuestas Lean Kata
                validation_results = await self._validate_response(
                    llm_response.content,
                    response_type
                )
                
                enriched_response = self._enrich_response_metadata(
                    llm_response,
                    search_results,
                    validation_results
                )
                
                enriched_response.metadata.update({
                    'text': llm_response.content,
                    'original_query': query,
                    'search_context': context
                })
                
                return enriched_response
            else:
                # Metadata simple para respuestas generales
                llm_response.metadata = {
                    'text': llm_response.content,
                    'type': 'general',
                    'metadata': base_metadata['metadata'],
                    'section_id': 'general'
                }
                return llm_response

        except Exception as e:
            logger.error(f"Error en el orquestador RAG: {str(e)}")
            raise

    async def _search_relevant_docs(
        self,
        query: str,
        metadata: Optional[Dict[str, str]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        from app.retriever.types import BoardSection

        # Creamos un objeto BoardSection para pasarlo al Retriever
        board_section = BoardSection(
            content=query,
            metadata=metadata or {}
        )

        # Usamos el método process_content del RetrieverSystem
        retriever_response = await self.retriever.process_content(
            board_content=board_section,
            max_results=top_k
        )

        # Extraemos los resultados del response
        return retriever_response.search_results


    async def _build_context(
        self,
        search_results: List[SearchResult]
    ) -> Dict[str, Any]:
        """
        Construye el contexto para el LLM a partir de los resultados de búsqueda
        """
        context = {
            "relevant_texts": [],
            "metadata": {}
        }
        
        total_tokens = 0
        
        for result in search_results:
            # Añadir texto si cabe en la ventana de contexto
            if total_tokens + len(result.text.split()) <= self.context_window:
                context["relevant_texts"].append({
                    "text": result.text,
                    "score": result.score,
                    "id": result.id
                })
                total_tokens += len(result.text.split())
                
                # Agregar metadatos relevantes
                if result.metadata:
                    section_id = result.metadata.get('section_id')
                    if section_id:
                        context["metadata"][section_id] = result.metadata
        
        return context

    async def _validate_response(
        self,
        content: str,
        response_type: ResponseType
    ) -> Dict[str, bool]:
        """
        Valida la respuesta del LLM
        """
        try:
            # Procesar la validación inicial
            validation_results = self.validator.process_validation(content)
            
            # Si el tipo de respuesta es validación, añadir validaciones específicas
            if response_type == ResponseType.VALIDATION:
                criteria = self.llm.validation_criteria.get(response_type.value, {})
                for key, criterion in criteria.items():
                    validation_results[key] = criterion in content.lower()
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error en validación de respuesta: {e}")
            return {"validation_error": str(e)}  

    def _enrich_response_metadata(
        self,
        response: LLMResponse,
        search_results: List[Dict[str, Any]],
        validation_results: Dict[str, bool]
    ) -> LLMResponse:
        """
        Enriquece los metadatos de la respuesta
        """
        if not response.metadata:
            response.metadata = {}
                
        # Añadir información de fuentes
        response.metadata["sources"] = [
            {
                "id": result['id'],  # Usar notación de diccionario
                "score": result['score'],  # Usar notación de diccionario
                "metadata": result.get('metadata', {})  # Usar .get() con valor por defecto
            } for result in search_results
        ]
        
        # Añadir resultados de validación
        response.metadata["validation"] = validation_results
        
        # Añadir confianza promedio basada en scores de búsqueda
        if search_results:
            response.confidence = sum(result['score'] for result in search_results) / len(search_results)
        
        return response
    
    async def validate_board_section(self, category: str, content: str) -> LLMResponse:
        """
        Valida el contenido de una categoría específica del tablero Lean Kata.
        Actúa como envoltorio para la función correspondiente del LLM.
        """
        return await self.llm.validate_board_section(category, content)

    async def get_section_suggestions(self, category: str, content: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """
        Obtiene sugerencias de mejora para una categoría específica del tablero Lean Kata.
        Actúa como envoltorio para la función correspondiente del LLM.
        """
        return await self.llm.get_section_suggestions(category, content, context)
    
    def process_board_request(
        self,
        board_id: str,
        section_type: str,
        content: dict,
        context: dict
    ) -> Awaitable[LLMResponse]:
        """
        Procesa la petición del tablero simulando la llamada de la API.
        Convierte el board_content en un query y metadata adecuados.
        """
        query = f"{content.get('title', '')}\n{content.get('description', '')}"

        # Inicializar metadata correctamente, manejando casos donde section_type o category no estén definidos
        metadata = {"category": section_type.lower() if section_type else "default", "board_id": board_id}
        
        # Convertir cada valor de context a string y agregarlo a metadata
        metadata.update({k: str(v) for k, v in context.items()})

        return self.process_query(
            query=query,
            response_type="validation",  # Asegúrate de usar minúsculas para el enum
            metadata=metadata,
            language="es"
        )