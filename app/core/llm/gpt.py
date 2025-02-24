import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
import json
import openai
import logging
from typing import Dict, List, Optional
from .types import LLMRequest, LLMResponse, ResponseType
from .temperature import TemperatureManager
from .validator import ResponseValidator
from core.orchestrator.query_classifier import QueryClassifier  # Importación del clasificador de consultas


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMModule:
    def __init__(self, model: str = "gpt-4o-mini"):
        """Inicializa el módulo LLM usando la API key desde las variables de entorno"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API Key not found in .env file")
        
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
        self.temp_manager = TemperatureManager()
        self.validator = ResponseValidator()

        # Agregar esta línea para inicializar el query_classifier
        self.query_classifier = QueryClassifier()

        # System prompts originales para diferentes propósitos
        self.system_prompts = {
            ResponseType.CHAT: """Eres un asistente experto en metodología Lean Kata, especializado en guiar a usuarios a través del proceso de mejora continua. Tu objetivo es ayudar a mantener el enfoque en el aprendizaje científico y la experimentación sistemática.

Debes:
- Mantener las conversaciones alineadas con los principios Lean Kata
- Fomentar el pensamiento experimental y la validación de hipótesis
- Ayudar a identificar métricas relevantes y objetivos SMART
- Promover la documentación clara de aprendizajes y resultados

Evita:
- Sugerir soluciones directas sin proceso de experimentación
- Permitir objetivos vagos o no medibles
- Ignorar la importancia del aprendizaje en el proceso""",

            ResponseType.VALIDATION: """Eres un validador experto en metodología Lean Kata, encargado de asegurar que cada elemento del tablero cumpla con los criterios y mejores prácticas establecidas.

Para cada tipo de entrada debes verificar:

Challenge:
- Debe ser específico y relevante para la organización
- Debe representar una brecha significativa entre la situación actual y la deseada

Target:
- Debe ser SMART (Específico, Medible, Alcanzable, Relevante, Temporal)
- Debe estar alineado con el Challenge
- Debe incluir métricas claras y fecha objetivo

Obstacle:
- Debe ser específico y actual
- Debe estar directamente relacionado con el Target
- No debe ser una solución disfrazada de obstáculo

Experiment:
- Debe estar relacionado con un obstáculo específico
- Debe ser pequeño y rápido de implementar
- Debe tener una hipótesis clara y medible

Hypothesis:
- Debe ser específica y comprobable
- Debe incluir predicciones cuantificables
- Debe estar relacionada con el experimento propuesto

Process:
- Debe ser detallado y secuencial
- Debe incluir responsables y plazos
- Debe ser realista y ejecutable

Results:
- Deben ser cuantitativos cuando sea posible
- Deben estar relacionados con la hipótesis
- Deben incluir datos relevantes

Learnings:
- Deben estar basados en evidencia
- Deben relacionarse con la hipótesis original
- Deben ser accionables

Mental Contrast:
- Debe incluir tanto resultados positivos como obstáculos
- Debe ser realista y específico
- Debe estar alineado con el Target

Task:
- Debe ser específica y accionable
- Debe tener un responsable claro
- Debe incluir un plazo definido

Tribe:
- Debe incluir roles claros
- Debe tener un coach identificado
- Debe especificar frecuencia de reuniones

Retorna un objeto JSON con la validación de cada criterio y sugerencias de mejora específicas.""",

            ResponseType.SUGGESTION: """Eres un consejero experto en metodología Lean Kata, especializado en proporcionar sugerencias constructivas para mejorar cada elemento del tablero.

Contexto del rol:
- Debes basar tus sugerencias en mejores prácticas de Lean Kata
- Tus recomendaciones deben ser específicas y accionables
- Debes mantener el enfoque en el aprendizaje y la mejora continua

Para cada elemento del tablero, proporciona sugerencias que:
- Mejoren la claridad y especificidad
- Fortalezcan la alineación con los principios Lean Kata
- Aumenten la medibilidad y capacidad de seguimiento
- Fomenten el aprendizaje y la experimentación

Formula tus sugerencias de manera constructiva, iniciando con frases como:
- "Considera agregar..."
- "Podrías fortalecer esto mediante..."
- "Una forma de mejorar sería..."
- "Para hacer esto más medible..."

Evita:
- Críticas no constructivas
- Sugerencias vagas o generales
- Recomendaciones que se desvíen de la metodología Lean Kata""",

            ResponseType.DOCUMENTATION: """Eres un especialista en documentación de proyectos Lean Kata, encargado de generar documentación clara, estructurada y útil.

Tu objetivo es:
- Crear documentación que capture el proceso completo de mejora
- Resaltar los aprendizajes clave y resultados
- Mantener la trazabilidad del proceso experimental
- Facilitar la transferencia de conocimiento

La documentación debe incluir:
1. Resumen Ejecutivo
   - Challenge y Target principales
   - Resultados clave alcanzados
   - Aprendizajes fundamentales

2. Proceso de Mejora
   - Línea temporal de experimentos
   - Evolución de hipótesis y resultados
   - Obstáculos encontrados y superados

3. Resultados y Métricas
   - Datos cuantitativos y cualitativos
   - Comparación antes/después
   - Impacto en KPIs relevantes

4. Lecciones Aprendidas
   - Insights principales
   - Mejores prácticas identificadas
   - Recomendaciones para futuros proyectos

5. Anexos
   - Detalles de experimentos
   - Datos completos
   - Referencias y recursos utilizados"""
        }

        # Prompt para consultas generales
        self.general_prompt = """Eres un asistente AI versátil y servicial. Tu objetivo es proporcionar respuestas claras, precisas y útiles para cualquier tipo de consulta.

Cuando se te pregunte sobre temas generales (no relacionados con Lean Kata):
- Proporciona información precisa y relevante
- Mantén un tono conversacional y profesional
- Adapta el nivel de detalle según la consulta
- Sé claro y directo en tus explicaciones

Si la pregunta es ambigua, solicita clarificación. Si no tienes información suficiente sobre un tema, indícalo claramente."""

        # Criterios de validación para cada sección del tablero
        self.validation_criteria = {
            "challenge": {
                "specific": "El desafío debe ser específico y claro",
                "relevant": "Debe ser relevante para la organización",
                "measurable": "Debe ser medible o verificable"
            },
            "target": {
                "smart": "Debe seguir criterios SMART",
                "aligned": "Debe alinearse con el Challenge",
                "metrics": "Debe incluir métricas claras"
            },
            "experiment": {
                "specific": "Debe ser específico y enfocado en un solo cambio",
                "testable": "Debe ser fácilmente testeable",
                "quick": "Debe ser rápido de implementar",
                "relevant": "Debe abordar directamente un obstáculo identificado"
            },
            "hypothesis": {
                "testable": "Debe ser comprobable y medible",
                "specific": "Debe ser específica y clara",
                "predictive": "Debe incluir una predicción concreta",
                "related": "Debe estar relacionada con el experimento"
            }
        }

    def _get_query_classifier(self):
        """
        Lazy import of QueryClassifier to avoid circular imports
        This method imports the QueryClassifier only when it's needed
        """
        from app.orchestrator.query_classifier import QueryClassifier
        return QueryClassifier()

    async def process_request(self, request: LLMRequest) -> LLMResponse:
        """Procesa una solicitud al LLM"""
        try:
            # Ensure context is a dictionary if it's None
            request.context = request.context or {}

            # Lazy import of query classifier
            query_classifier = self._get_query_classifier()
            
            # Determinar si es consulta Lean Kata o general
            is_lean_kata = (
                request.context and 
                request.context.get('metadata', {}).get('query_type') == 'lean_kata'
            )
            
            # Clasificar la consulta si no se ha hecho
            if not is_lean_kata:
                is_lean_kata, query_metadata = self.query_classifier.classify_query(request.query)
                request.context['metadata'] = query_metadata['metadata']
            
            # Seleccionar prompt apropiado
            if is_lean_kata:
                system_prompt = self.system_prompts[request.response_type]
                temperature = self.temp_manager.get_temperature(
                    request.response_type, 
                    request.temperature
                )
            else:
                system_prompt = self.general_prompt
                temperature = 0.7  # Temperatura estándar para consultas generales
            
            # Preparar mensajes
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Añadir contexto si existe
            if request.context:
                messages.append({
                    "role": "system", 
                    "content": f"Contexto: {json.dumps(request.context, ensure_ascii=False)}"
                })
            
            messages.append({"role": "user", "content": request.query})
            
            # Realizar llamada a la API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Metadata consistente
            metadata = {
                'text': content,
                'type': 'lean_kata' if is_lean_kata else 'general',
                'metadata': {
                    'model': self.model,
                    'temperature': temperature,
                    'tokens_used': response.usage.total_tokens,
                    'response_type': request.response_type.value,
                    'query_type': 'lean_kata' if is_lean_kata else 'general'
                },
                'section_id': 'lean_kata' if is_lean_kata else 'general'
            }
            
            # Procesar respuesta según el tipo
            if is_lean_kata:
                if request.response_type == ResponseType.VALIDATION:
                    validation_results = self.validator.process_validation(content)
                    return LLMResponse(
                        content=content,
                        metadata=metadata,
                        validation_results=validation_results
                    )
                elif request.response_type == ResponseType.SUGGESTION:
                    suggestions = self.validator.process_suggestions(content)
                    return LLMResponse(
                        content=content,
                        metadata=metadata,
                        suggestions=suggestions
                    )
            
            # Respuesta estándar
            return LLMResponse(
                content=content,
                metadata=metadata,
                confidence=request.context.get('metadata', {}).get('confidence', 0.7)
            )

        except Exception as e:
            logger.error(f"Error procesando LLM request: {str(e)}")
            raise

    async def validate_board_section(self, category: str, content: str) -> Dict:
        """Valida una sección específica del tablero Lean Kata"""
        criteria = self.validation_criteria.get(category, {})
        validation_prompt = f"Evalúa el siguiente contenido para la categoría {category} del tablero Lean Kata:\n\n{content}\n\nCriterios:\n"
        
        for key, criterion in criteria.items():
            validation_prompt += f"- {criterion}\n"
        
        request = LLMRequest(
            query=validation_prompt,
            response_type=ResponseType.VALIDATION,
            context={
                'metadata': {
                    'category': category,
                    'query_type': 'lean_kata'
                }
            }
        )
        
        return await self.process_request(request)

    async def get_section_suggestions(
        self, 
        category: str, 
        content: str, 
        context: Optional[Dict] = None
    ) -> LLMResponse:
        """Obtiene sugerencias de mejora para una sección"""
        suggestion_prompt = f"Analiza el siguiente contenido de la categoría {category} y proporciona sugerencias de mejora específicas:\n\n{content}"
        
        metadata = {
            'category': category,
            'query_type': 'lean_kata',
            **(context or {})
        }
        
        request = LLMRequest(
            query=suggestion_prompt,
            response_type=ResponseType.SUGGESTION,
            context={'metadata': metadata}
        )
        
        return await self.process_request(request)

    async def generate_documentation(self, project_data: Dict) -> LLMResponse:
        """Genera documentación para un proyecto"""
        request = LLMRequest(
            query="Genera un reporte detallado del proyecto.",
            response_type=ResponseType.DOCUMENTATION,
            context={
                'metadata': {
                    'query_type': 'lean_kata',
                    **project_data
                }
            }
        )
        return await self.process_request(request)

    async def generate_experiment_tasks(self, experiment_data: Dict) -> LLMResponse:
        """Genera tareas específicas para un experimento"""
        task_prompt = f"""
        Basado en el siguiente experimento:
        {json.dumps(experiment_data, ensure_ascii=False)}
        
        Genera una lista detallada de tareas específicas necesarias para su implementación.
        Cada tarea debe incluir:
        - Descripción clara
        - Responsable sugerido
        - Tiempo estimado
        - Dependencias (si las hay)
        """
        
        request = LLMRequest(
            query=task_prompt,
            response_type=ResponseType.DOCUMENTATION,
            context={
                'metadata': {
                    'query_type': 'lean_kata',
                    **experiment_data
                }
            }
        )
        return await self.process_request(request)