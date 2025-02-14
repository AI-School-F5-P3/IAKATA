from typing import Dict, List, Optional, Tuple
from app.llm.types import ResponseType, LLMRequest, LLMResponse
from app.llm.gpt import LLMModule
from app.vectorstore.vector_store import VectorStore
from app.vectorstore.common_types import TextType, ProcessedText
from app.vectorstore.metadata_manager import MetadataManager
import json
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    def __init__(self):
        """Inicializa el orquestador RAG"""
        self.vector_store = VectorStore()
        self.llm = LLMModule()
        self.metadata_manager = MetadataManager()
        
    async def process_board_request(
        self, 
        board_id: str,
        section_type: str,
        content: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Procesa una petición relacionada con un tablero
        
        Args:
            board_id: Identificador del tablero
            section_type: Tipo de sección (challenge, target, etc.)
            content: Contenido del tablero
            context: Contexto adicional opcional
            
        Returns:
            Dict con la respuesta procesada
        """
        try:
            # 1. Preparar contexto de búsqueda
            search_context = self._prepare_search_context(section_type, content)
            logger.info(f"Contexto de búsqueda preparado para {board_id}")

            # 2. Realizar búsqueda semántica
            relevant_chunks = await self._retrieve_relevant_context(
                search_context=search_context,
                board_id=board_id,
                section_type=section_type
            )
            logger.info(f"Recuperados {len(relevant_chunks)} chunks relevantes")

            # 3. Generar prompt enriquecido
            prompt = self._build_prompt(
                section_type=section_type,
                content=content,
                context=context,
                relevant_chunks=relevant_chunks
            )
            
            logger.info(f"Building prompt with context:")
            logger.info(f"Section type: {section_type}")
            logger.info(f"Content: {content}")
            logger.info(f"Relevant chunks: {json.dumps(relevant_chunks, indent=2)}")

            prompt = self._build_prompt(
                section_type=section_type,
                content=content,
                context=context,
                relevant_chunks=relevant_chunks
            )

            logger.info(f"Final prompt:\n{prompt}")

            # Procesar con LLM
            response_type = self._determine_response_type(section_type)
            llm_context = self._build_llm_context(board_id, section_type, context)

            logger.info(f"LLM context: {json.dumps(llm_context, indent=2)}")

            llm_response = await self.llm.process_request(
                LLMRequest(
                    query=prompt,
                    response_type=response_type,
                    context=llm_context
                )
            )

            # 4. Procesar con LLM
            response_type = self._determine_response_type(section_type)
            llm_response = await self.llm.process_request(
                LLMRequest(
                    query=prompt,
                    response_type=response_type,
                    context=self._build_llm_context(board_id, section_type, context)
                )
            )

            return self._format_response(llm_response, relevant_chunks)

        except Exception as e:
            logger.error(f"Error procesando petición de tablero: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "board_id": board_id
            }

    def _determine_response_type(self, section_type: str) -> ResponseType:
        """Determina el tipo de respuesta basado en la sección"""
        validation_sections = ['challenge', 'target', 'hypothesis']
        if section_type in validation_sections:
            return ResponseType.VALIDATION
        return ResponseType.SUGGESTION

    async def _retrieve_relevant_context(
        self,
        search_context: Dict,
        board_id: str,
        section_type: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Recupera chunks relevantes usando búsqueda híbrida
        """
        try:
            # Construir query
            query = self._build_search_query(
                context=search_context,
                section_type=section_type
            )

            # Realizar búsqueda híbrida
            results = self.vector_store.hybrid_search(
                query=query,
                top_k=top_k
            )

            # Enriquecer resultados con metadata
            enriched_results = []
            for result in results:
                metadata = self.metadata_manager.get_entry(result['id'])
                if metadata:
                    result['metadata'] = metadata
                    enriched_results.append(result)

            return enriched_results

        except Exception as e:
            logger.error(f"Error recuperando contexto: {str(e)}")
            return []

    def _prepare_search_context(
        self,
        section_type: str,
        content: Dict
    ) -> Dict:
        """Prepara el contexto para la búsqueda"""
        return {
            "type": section_type,
            "content": content,
            "text": self._extract_searchable_text(content)
        }

    def _extract_searchable_text(self, content: Dict) -> str:
        """Extrae texto para búsqueda del contenido"""
        searchable_fields = ['title', 'description', 'objective', 'notes']
        text_parts = []
        
        for field in searchable_fields:
            if field in content and content[field]:
                text_parts.append(str(content[field]))
                
        return " ".join(text_parts)

    def _build_search_query(self, context: Dict, section_type: str) -> str:
        """Construye la query de búsqueda"""
        section_prefixes = {
            'challenge': 'reto lean kata',
            'target': 'objetivo lean kata',
            'hypothesis': 'hipótesis lean kata',
            'experiment': 'experimento lean kata'
        }
        
        prefix = section_prefixes.get(section_type, 'lean kata')
        return f"{prefix}: {context['text']}"

    def _build_prompt(
        self,
        section_type: str,
        content: Dict,
        context: Optional[Dict],
        relevant_chunks: List[Dict]
    ) -> str:
        """Construye el prompt enriquecido para el LLM"""
        # Base prompt
        prompt = f"Analiza el siguiente contenido de la sección '{section_type}' del tablero Lean Kata:\n\n"
        prompt += f"{content}\n\n"

        # Añadir contexto relevante
        if relevant_chunks:
            prompt += "Contexto relevante de la metodología:\n"
            for chunk in relevant_chunks:
                prompt += f"- {chunk['text']}\n"

        # Añadir instrucciones específicas por tipo
        prompt += self._get_section_instructions(section_type)

        return prompt

    def _get_section_instructions(self, section_type: str) -> str:
        """Obtiene instrucciones específicas por tipo de sección"""
        instructions = {
            'challenge': """
Evalúa si el reto cumple con:
1. Es específico y medible
2. Representa una brecha significativa
3. Está alineado con objetivos organizacionales
            """,
            'target': """
Verifica que el objetivo sea SMART:
- Específico: claramente definido
- Medible: con métricas concretas
- Alcanzable: realista
- Relevante: alineado con el reto
- Temporal: con plazo definido
            """,
            'hypothesis': """
Valida que la hipótesis:
1. Sea específica y verificable
2. Incluya predicción medible
3. Se base en evidencia
4. Se relacione con el experimento
            """
        }
        return instructions.get(section_type, "Analiza el contenido y sugiere mejoras.")

    def _build_llm_context(
        self,
        board_id: str,
        section_type: str,
        context: Optional[Dict]
    ) -> Dict:
        """Construye el contexto para el LLM"""
        llm_context = {
            "board_id": board_id,
            "section_type": section_type
        }
        
        if context:
            llm_context.update(context)
            
        return llm_context

    def _format_response(
        self,
        llm_response: Optional[LLMResponse],
        relevant_chunks: List[Dict]
    ) -> Dict:
        """Formatea la respuesta final"""
        try:
            # Asegurar una estructura base
            response = {
                "content": None,
                "metadata": {
                    "llm_metadata": {},
                    "vector_results": []
                }
            }

            # Si hay respuesta válida, actualizar el contenido
            if llm_response and llm_response.validation_results:
                response["validation_results"] = {
                "validations": llm_response.validation_results.validations,
                "suggestions": llm_response.validation_results.suggestions
    }

            # Añadir resultados vectoriales si existen
            if relevant_chunks:
                response["metadata"]["vector_results"] = [
                    {
                        "text": chunk.get("text", ""),
                        "score": chunk.get("score", 0.0),
                        "type": chunk.get("metadata", {}).get("type", "unknown")
                    }
                    for chunk in relevant_chunks[:1]  # Solo el más relevante
                ]

            # Añadir validaciones y sugerencias si existen
            if llm_response and llm_response.validation_results:
                response["validation_results"] = {
                    "validation": llm_response.validation_results.validations,
                    "suggestions": llm_response.validation_results.suggestions
                }

            return response

        except Exception as e:
            logger.error(f"Error formateando respuesta: {str(e)}")
            # Retornar una estructura base válida incluso en caso de error
            return {
                "content": str(e) if not llm_response else llm_response.content,
                "metadata": {
                    "llm_metadata": {"error": str(e)},
                    "vector_results": []
                },
                "error": str(e)
            }