import os
from dotenv import load_dotenv
import json
import openai
import logging
from typing import Dict, List, Optional
from .types import LLMRequest, LLMResponse, ResponseType
from .temperature import TemperatureManager
from .validator import ResponseValidator

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMModule:
    def __init__(self, model: str = "gpt-4"):
        """Inicializa el módulo LLM usando la API key desde las variables de entorno"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API Key not found in .env file")
        
        self.model = model
        openai.api_key = self.api_key
        self.temp_manager = TemperatureManager()
        self.validator = ResponseValidator()
        
        # System prompts for different contexts
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
        
        # Validation criteria for each board section
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
            },
            "learnings": {
                "evidence_based": "Debe basarse en evidencia concreta",
                "actionable": "Debe ser accionable para futuros experimentos",
                "related": "Debe relacionarse con la hipótesis planteada",
                "clear": "Debe ser claro y específico"
            },
            "mental_contrast": {
                "balanced": "Debe incluir tanto aspectos positivos como negativos",
                "realistic": "Debe ser realista y basado en hechos",
                "specific": "Debe ser específico y detallado",
                "actionable": "Debe conducir a acciones concretas"
            },
            "obstacle": {
                "current": "Debe ser un obstáculo actual y real",
                "specific": "Debe ser específico y bien definido",
                "relevant": "Debe estar relacionado con el target",
                "not_solution": "No debe ser una solución disfrazada"
            },
            "process": {
                "sequential": "Debe ser secuencial y lógico",
                "detailed": "Debe incluir pasos detallados",
                "assignable": "Debe tener responsables claros",
                "timebound": "Debe incluir plazos definidos"
            },
            "results": {
                "quantitative": "Debe incluir datos cuantitativos cuando sea posible",
                "complete": "Debe ser completo y detallado",
                "relevant": "Debe relacionarse con la hipótesis",
                "verifiable": "Debe ser verificable"
            },
            "task": {
                "specific": "Debe ser específica y clara",
                "assignable": "Debe tener un responsable definido",
                "timebound": "Debe tener un plazo establecido",
                "achievable": "Debe ser realizable con los recursos disponibles"
            },
            "tribe": {
                "roles": "Debe definir roles claros",
                "coach": "Debe identificar al coach del equipo",
                "meetings": "Debe especificar frecuencia de reuniones",
                "responsibilities": "Debe establecer responsabilidades claras"
            }
        }

    def _prepare_messages(self, request: LLMRequest) -> List[Dict]:
        """Prepare the message list for the OpenAI API call"""
        messages = [
            {"role": "system", "content": self.system_prompts[request.response_type]}
        ]
        
        if request.context:
            context_str = json.dumps(request.context, ensure_ascii=False)
            messages.append({"role": "system", "content": f"Contexto: {context_str}"})
        
        messages.append({"role": "user", "content": request.query})
        return messages

    async def process_request(self, request: LLMRequest) -> LLMResponse:
        """Process an LLM request and return a response"""
        try:
            temperature = self.temp_manager.get_temperature(
                request.response_type, 
                request.temperature
            )
            
            messages = self._prepare_messages(request)
            
            client = openai.OpenAI()

            logger.debug(f"Sending request to OpenAI - Model: {self.model}, Temperature: {temperature}")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            metadata = {
                "model": self.model,
                "response_type": request.response_type.value,
                "temperature": temperature,
                "tokens_used": response.usage.total_tokens
            }
            
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
            
            return LLMResponse(
                content=content,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error processing LLM request: {str(e)}")
            raise

    async def validate_board(self, board_data: Dict) -> LLMResponse:
        """Validate a board's content"""
        request = LLMRequest(
            query=f"Valida el siguiente tablero Lean Kata: {json.dumps(board_data, ensure_ascii=False)}",
            response_type=ResponseType.VALIDATION,
            context={"board_type": board_data.get("type", "unknown")}
        )
        return await self.process_request(request)

    async def validate_board_section(self, section_type: str, content: str) -> Dict:
        """Validate a specific section of the Lean Kata board"""
        criteria = self.validation_criteria.get(section_type, {})
        validation_prompt = f"Evalúa el siguiente contenido para la sección {section_type} del tablero Lean Kata:\n\n{content}\n\nCriterios:\n"
        for key, criterion in criteria.items():
            validation_prompt += f"- {criterion}\n"
        
        request = LLMRequest(
            query=validation_prompt,
            response_type=ResponseType.VALIDATION,
            context={"section_type": section_type}
        )
        return await self.process_request(request)

    async def get_section_suggestions(self, section_type: str, content: str, context: Optional[Dict] = None) -> LLMResponse:
        """Get improvement suggestions for a specific board section"""
        suggestion_prompt = f"Analiza el siguiente contenido de la sección {section_type} y proporciona sugerencias de mejora específicas:\n\n{content}"
        
        request = LLMRequest(
            query=suggestion_prompt,
            response_type=ResponseType.SUGGESTION,
            context={
                "section_type": section_type,
                "board_context": context or {}
            }
        )
        return await self.process_request(request)

    async def generate_suggestions(self, context: Dict) -> LLMResponse:
        """Generate suggestions based on current context"""
        request = LLMRequest(
            query="Genera sugerencias de mejora basadas en el contexto proporcionado.",
            response_type=ResponseType.SUGGESTION,
            context=context
        )
        return await self.process_request(request)

    async def generate_documentation(self, project_data: Dict) -> LLMResponse:
        """Generate documentation for a project"""
        request = LLMRequest(
            query="Genera un reporte detallado del proyecto.",
            response_type=ResponseType.DOCUMENTATION,
            context=project_data
        )
        return await self.process_request(request)

    async def generate_experiment_tasks(self, experiment_data: Dict) -> LLMResponse:
        """Generate specific tasks for an experiment"""
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
            context=experiment_data
        )
        return await self.process_request(request)