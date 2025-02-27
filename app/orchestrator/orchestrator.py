# app/orchestrator/orchestrator.py

from typing import Dict, List, Optional, Any, Awaitable
from datetime import datetime
import logging

# Imports de documentación
from app.documentation.generator import DocumentGenerator
from app.documentation.template_manager import TemplateStyleManager
from app.documentation.storage import DocumentStorage
from app.documentation.types import Document, DocumentFormat

# Imports existentes
from .query_classifier import QueryClassifier
from app.vectorstore.vector_store import VectorStore
from app.vectorstore.common_types import TextType, ProcessedText
from app.llm.types import LLMRequest, LLMResponse, ResponseType
from app.llm.gpt import LLMModule
from app.llm.validator import ResponseValidator
from app.retriever.types import SearchQuery, SearchResult, BoardSection
from app.retriever.retriever import RetrieverSystem

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    def __init__(
        self,
        vector_store: VectorStore,
        llm: LLMModule,
        validator: ResponseValidator,
        doc_generator=None,
        template_manager=None,
        doc_storage=None
    ):
        self.vector_store = vector_store
        self.llm = llm
        self.validator = validator
        self.query_classifier = QueryClassifier()
        self.context_window = 4000
        
        # Componentes de documentación
        self.doc_generator = doc_generator
        self.template_manager = TemplateStyleManager()
        self.doc_storage = doc_storage
        
        # Inicializar retriever
        self.retriever = RetrieverSystem(vector_store)

    async def process_query(
        self,
        query: str,
        response_type: ResponseType,
        top_k: int = 5,
        temperature: Optional[float] = None,
        language: str = "es",
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Procesa una consulta determinando si usar RAG para Lean Kata o respuesta general"""
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

    async def generate_documentation(
        self,
        project_data: Dict,
        template_id: str = "project_report",
        format: Optional[DocumentFormat] = None
    ) -> Document:
        """Genera documentación estructurada para un proyecto"""
        try:
            # 1. Búsqueda de documentos relevantes usando el sistema existente
            enriched_context = await self._build_documentation_context(project_data)

            # 2. Obtener y validar template
            if not self.template_manager:
                raise ValueError("Template manager no configurado")
            
            template = self.template_manager.create_document_template(template_id)
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
            logger.error(f"Error en generate_documentation: {str(e)}")
            raise

    async def _build_documentation_context(self, project_data: Dict) -> Dict:
        """Construye el contexto enriquecido para la documentación"""
        try:
            search_query = self._extract_search_terms(project_data)
            metadata = {
                "type": "documentation",
                "category": "general",
                "project_type": project_data.get("type", "challenge")
            }

            # Intentar búsqueda pero continuar incluso si no hay resultados
            search_results = await self._search_relevant_docs(
                query=search_query,
                metadata=metadata,
                top_k=5
            )

            # Construir contexto incluso sin resultados
            enriched_context = {
                "project_data": project_data,
                "relevant_documents": search_results or [],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "source": "RAG System",
                    "project_type": project_data.get("type", "challenge")
                }
            }

            return enriched_context

        except Exception as e:
            logger.error(f"Error construyendo contexto de documentación: {str(e)}")
            return {
                "project_data": project_data,
                "relevant_documents": [],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
            }

    async def _search_relevant_docs(
        self,
        query: str,
        metadata: Optional[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Busca documentos relevantes usando el retriever"""
        try:
            # Asegurar que metadata tenga una categoría
            if metadata is None:
                metadata = {}
            if 'category' not in metadata:
                metadata['category'] = 'general'
            
            # Limpiar metadata para crear BoardSection
            board_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    board_metadata[key] = value
                else:
                    # Convertir valores complejos a string para evitar errores de validación
                    board_metadata[key] = str(value)
            
            # Crear BoardSection para el retriever
            board_section = BoardSection(
                content=query,
                metadata=board_metadata
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
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Construye el contexto para el LLM a partir de los resultados de búsqueda"""
        context = {
            "relevant_texts": [],
            "metadata": {}
        }
        
        total_tokens = 0
        
        for result in search_results:
            if total_tokens + len(result["text"].split()) <= self.context_window:
                context["relevant_texts"].append({
                    "text": result["text"],
                    "score": result["score"],
                    "id": result["id"]
                })
                total_tokens += len(result["text"].split())
                
                if result.get("metadata"):
                    section_id = result["metadata"].get('section_id')
                    if section_id:
                        context["metadata"][section_id] = result["metadata"]
        
        return context

    def _extract_search_terms(self, project_data: Dict) -> str:
        """Extrae términos relevantes del proyecto para la búsqueda"""
        search_terms = []
        
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

        return " ".join(filter(None, search_terms))

    async def _validate_response(
        self,
        content: str,
        response_type: ResponseType
    ) -> Dict[str, bool]:
        """Valida la respuesta del LLM"""
        try:
            validation_results = self.validator.process_validation(content)
            
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
        """Enriquece los metadatos de la respuesta"""
        if not response.metadata:
            response.metadata = {}
                
        response.metadata["sources"] = [
            {
                "id": result['id'],
                "score": result['score'],
                "metadata": result.get('metadata', {})
            } for result in search_results
        ]
        
        response.metadata["validation"] = validation_results
        
        if search_results:
            response.confidence = sum(result['score'] for result in search_results) / len(search_results)
        
        return response

    async def validate_board_section(self, category: str, content: str) -> LLMResponse:
        """Valida el contenido de una categoría específica del tablero Lean Kata"""
        return await self.llm.validate_board_section(category, content)

    async def get_section_suggestions(
        self,
        category: str,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """Obtiene sugerencias de mejora para una categoría específica"""
        return await self.llm.get_section_suggestions(category, content, context)
    
    # Modificación en process_board_request en orchestrator.py
    def process_board_request(
        self,
        section_type: str,
        content: dict,
        context: dict
    ) -> Awaitable[LLMResponse]:
        """Procesa la petición del tablero"""

        query = content

        # Determinar el tipo de respuesta basado en el contexto
        response_type = ResponseType.VALIDATION
        if context.get("response_type") == "concise":
            response_type = ResponseType.CHAT

        metadata = {
            "category": section_type.lower() if section_type else "default",
        }
        metadata.update({k: str(v) for k, v in context.items()})

        return self.process_query(
            query=query,
            response_type=response_type,  
            metadata=metadata,
            language="es"
        )