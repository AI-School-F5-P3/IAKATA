# En app/orchestrator/orchestrator.py

from typing import Dict, List, Optional, Any, Awaitable
from datetime import datetime
import logging

# Imports de documentación
from app.documentation.generator import DocumentGenerator
from app.documentation.templates import TemplateManager
from app.documentation.storage import DocumentStorage
from app.documentation.types import Document, DocumentFormat

# Imports existentes
from app.retriever.retriever import RetrieverSystem
from app.vectorstore.common_types import TextType, ProcessedText
from app.llm.types import LLMRequest, LLMResponse, ResponseType
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.retriever.types import SearchQuery, SearchResult
from app.retriever.types import BoardSection

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    def __init__(self, vector_store, llm, validator, 
                 doc_generator=None, template_manager=None, doc_storage=None):
        self.retriever = RetrieverSystem(vector_store)
        self.llm = llm
        self.validator = validator
        self.context_window = 4000  # Tamaño máximo del contexto para el LLM
        self.doc_generator = doc_generator or DocumentGenerator(llm)
        self.template_manager = template_manager or TemplateManager()
        self.doc_storage = doc_storage

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
        
    async def generate_documentation(
        self,
        project_data: Dict,
        template_id: str = "project_report",
        format: DocumentFormat = DocumentFormat.MARKDOWN
    ) -> Document:
        """
        Genera documentación para un proyecto
        Args:
            project_data: Datos del proyecto
            template_id: ID del template a usar
            format: Formato de salida deseado
        Returns:
            Document generado
        """
        try:
            # 1. Búsqueda de documentos relevantes usando el sistema existente
            enriched_context = await self._build_documentation_context(project_data)

            # 2. Obtener y validar template
            if not self.template_manager:
                raise ValueError("Template manager no configurado")
            
            template = self.template_manager.get_template(template_id)
            if not template:
                raise ValueError(f"Template no encontrado: {template_id}")

            # 3. Generar documento usando DocumentGenerator
            if not self.doc_generator:
                self.doc_generator = DocumentGenerator(self.llm)

            document = await self.doc_generator.generate_document(
                template=template,
                context=enriched_context,
                format=format
            )

            # 4. Almacenar si hay storage configurado
            if self.doc_storage:
                doc_path = self.doc_storage.save_document(document)
                document.metadata = document.metadata or {}
                document.metadata["file_path"] = str(doc_path)

            return document
            
        except Exception as e:
            logger.error(f"Error generando documentación: {str(e)}")
            raise

    async def _build_documentation_context(self, project_data: Dict) -> Dict:
        """
        Construye el contexto enriquecido para la documentación
        usando el sistema RAG existente.
        """
        try:
            # 1. Extraer términos clave del proyecto para búsqueda
            search_query = self._extract_search_terms(project_data)

            # 2. Preparar metadata con tipo de documento y categoría
            metadata = {
                "type": "documentation",
                "category": "general",  # Categoría por defecto
                "project_type": project_data.get("type", "challenge")
            }

            # 3. Realizar búsqueda usando el retriever existente
            search_results = await self._search_relevant_docs(
                query=search_query,
                metadata=metadata,
                top_k=5
            )

            # 4. Construir contexto enriquecido
            enriched_context = {
                "project_data": project_data,
                "relevant_documents": search_results,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "source": "RAG System",
                    "project_type": project_data.get("type", "challenge")
                }
            }

            return enriched_context

        except Exception as e:
            logger.error(f"Error construyendo contexto de documentación: {str(e)}")
            raise

    def _extract_search_terms(self, project_data: Dict) -> str:
        """
        Extrae términos relevantes del proyecto para la búsqueda
        """
        search_terms = []
        
        # Extraer términos clave del proyecto
        if 'title' in project_data:
            search_terms.append(project_data['title'])
        if 'description' in project_data:
            search_terms.append(project_data['description'])
        if 'challenge' in project_data:
            if isinstance(project_data['challenge'], dict):
                search_terms.extend([
                    project_data['challenge'].get('description', ''),
                    project_data['challenge'].get('current_state', ''),
                    project_data['challenge'].get('target_state', '')
                ])
            else:
                search_terms.append(str(project_data['challenge']))

        # Unir términos en una query
        return " ".join(filter(None, search_terms))
    
    async def _search_relevant_docs(
        self,
        query: str,
        metadata: Optional[Dict[str, str]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        

        try:
        # Asegurar que metadata tenga una categoría
            if metadata is None:
                metadata = {}
            if 'category' not in metadata:
                metadata['category'] = 'general'
                
            # Crear BoardSection para el retriever
            board_section = BoardSection(
                content=query,
                metadata=metadata
            )

            # Procesar contenido
            retriever_response = await self.retriever.process_content(
                board_content=board_section,
                max_results=top_k
            )

            return retriever_response.search_results if retriever_response else []
            
        except Exception as e:
            logger.error(f"Error en búsqueda de documentos: {str(e)}")
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
    
    