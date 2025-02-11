import json
import openai
import logging
from typing import Dict, List
from .types import LLMRequest, LLMResponse, ResponseType
from .temperature import TemperatureManager
from .validator import ResponseValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMModule:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """Initialize the LLM module"""
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        self.temp_manager = TemperatureManager()
        self.validator = ResponseValidator()
        
        # System prompts for different contexts
        self.system_prompts = {
            ResponseType.CHAT: """Eres un asistente experto en metodología Lean Kata...""",
            ResponseType.VALIDATION: """Eres un validador de datos...""",
            ResponseType.SUGGESTION: """Eres un consejero experto...""",
            ResponseType.DOCUMENTATION: """Eres un especialista en documentación..."""
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
            
            response = await openai.ChatCompletion.acreate(
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