from typing import Dict, List, Optional, Any, Awaitable
from pydantic import BaseModel

from app.retriever.search import SearchEngine
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
        vector_store: SearchEngine,
        llm: LLMModule,
        validator: ResponseValidator
    ):
        self.vector_store = vector_store
        self.llm = llm
        self.validator = validator
        self.context_window = 4000  # Tamaño máximo del contexto para el LLM

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
        Procesa una consulta a través del pipeline RAG completo
        """
        try:
            # 1. Búsqueda de documentos relevantes
            search_results = await self._search_relevant_docs(
                query=query,
                metadata=metadata,
                top_k=top_k
            )

            # 2. Construcción del contexto
            context = {
                "relevant_texts": [],
                "metadata": {}
            }

            total_tokens = 0
            for result in search_results:
                # Verificar que estamos dentro del límite de contexto
                if total_tokens + len(result['text'].split()) <= self.context_window:
                    context["relevant_texts"].append({
                        "text": result['text'],
                        "score": result['score'],
                        "id": result['id']
                    })
                    total_tokens += len(result['text'].split())
                    
                    # Agregar metadatos si existen
                    if result.get('metadata'):
                        section_id = result['metadata'].get('section_id')
                        if section_id:
                            context["metadata"][section_id] = result['metadata']

            # 3. Preparación de la solicitud al LLM
            llm_request = LLMRequest(
                query=query,
                context=context,
                response_type=response_type,
                temperature=temperature,
                language=language
            )
            
            # 4. Obtención de respuesta del LLM
            llm_response = await self.llm.process_request(llm_request)
            
            # 5. Validación de la respuesta
            validation_results = await self._validate_response(
                llm_response.content,
                response_type
            )
            
            # 6. Enriquecimiento de metadatos
            enriched_response = self._enrich_response_metadata(
                llm_response,
                search_results,
                validation_results
            )
            
            return enriched_response

        except Exception as e:
            logger.error(f"Error en el orquestador RAG: {str(e)}")
            raise Exception(f"Error en el orquestador RAG: {str(e)}")

    async def _search_relevant_docs(
        self,
        query: str,
        metadata: Optional[Dict[str, str]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes en el vector store usando la metadata para filtrar
        """
        try:
            search_query = SearchQuery(
                text=query,
                metadata=metadata or {},
                max_results=top_k
            )
            
            search_engine = SearchEngine(self.vector_store)
            results = search_engine.hybrid_search(
            query=search_query.text,
            top_k=search_query.max_results
            )
            
            # Asegurarse de que los resultados tienen el formato correcto
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result['id'],
                    'text': result['text'],
                    'score': result['score'],
                    'metadata': result.get('metadata', {}),
                    'type': result.get('type', 'unknown')
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda de documentos relevantes: {str(e)}")
            return []


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
        try:
            if not response.metadata:
                response.metadata = {}
                    
            # Añadir información de fuentes
            # Añadir log para debug
            logger.info(f"Resultados de búsqueda recibidos: {len(search_results)}")
            
            response.metadata["sources"] = [
                {
                    "id": result['id'],
                    "score": result['score'],
                    "metadata": result.get('metadata', {})
                } for result in search_results
            ]
            
            # Añadir resultados de validación
            response.metadata["validation"] = validation_results
            
            # Añadir confianza promedio basada en scores de búsqueda
            if search_results:
                response.confidence = sum(result['score'] for result in search_results) / len(search_results)
                logger.info(f"Confianza calculada: {response.confidence}")
            
            return response
                
        except Exception as e:
            logger.error(f"Error enriqueciendo metadatos de respuesta: {e}")
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