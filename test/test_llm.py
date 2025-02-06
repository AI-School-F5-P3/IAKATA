import pytest
import json
from unittest.mock import Mock, patch
from typing import Dict
import asyncio
from unittest.mock import AsyncMock

# Importaciones absolutas desde el módulo llm
from app.llm import (
    LLMModule,
    LLMRequest,
    LLMResponse,
    ResponseType,
    TemperatureManager,
    ResponseValidator
)

# ====== FIXTURES ======

@pytest.fixture
def api_key():
    return "test-api-key"

@pytest.fixture
def mock_openai():
    with patch('openai.ChatCompletion') as mock:
        # Create AsyncMock for acreate
        async_mock = AsyncMock()
        async_mock.return_value = create_mock_completion("Test response")
        mock.acreate = async_mock
        yield mock

@pytest.fixture
def llm_module(api_key):
    """
    Crea una instancia del módulo LLM para usar en las pruebas
    Inicializa el módulo con una clave API de prueba
    """
    return LLMModule(api_key=api_key)

@pytest.fixture
def sample_board_data():
    """
    Proporciona datos de ejemplo de un tablero Lean Kata
    Incluye equipo, reto y KPIs para simular un caso real
    """
    return {
        "type": "principal",
        "team": "Equipo Innovación",
        "challenge": "Mejorar la eficiencia operativa",
        "kpis": [
            {"name": "Tiempo de proceso", "current": 30, "target": 20},
            {"name": "Calidad", "current": 85, "target": 95}
        ]
    }

# ====== FUNCIONES AUXILIARES ======

def create_mock_completion(content: str, total_tokens: int = 100):
    """
    Crea una respuesta simulada de OpenAI
    Params:
        content: El contenido de la respuesta
        total_tokens: Número de tokens utilizados
    """
    return Mock(
        choices=[Mock(message=Mock(content=content))],
        usage=Mock(total_tokens=total_tokens)
    )

async def async_mock_completion(*args, **kwargs):
    """Async mock for OpenAI API responses"""
    messages = kwargs.get('messages', [])
    user_message = next((m['content'] for m in messages if m['role'] == 'user'), '')
    
    if 'Valida el siguiente tablero' in user_message:
        content = '{"valid": true, "kpis_defined": true, "challenge_clear": true}'
    elif 'Genera sugerencias' in user_message:
        content = """
        - Sugerencia 1
        - Sugerencia 2
        """
    elif 'Genera un reporte' in user_message:
        content = "# Reporte del Proyecto\n\nResumen ejecutivo..."
    else:
        content = "Respuesta general de prueba"
    
    await asyncio.sleep(0.1)
    return create_mock_completion(content)

# ====== CASOS DE PRUEBA ======

@pytest.mark.asyncio
async def test_board_validation(llm_module, mock_openai, sample_board_data):
    """
    Prueba la validación de un tablero Lean Kata
    Verifica que:
    1. Se pueden validar los datos del tablero
    2. Se reciben resultados de validación correctos
    3. Los metadatos incluyen el tipo de respuesta correcto
    """
    # Simula una respuesta de validación exitosa
    mock_response = create_mock_completion(
        content='{"valid": true, "kpis_defined": true, "challenge_clear": true}'
    )
    mock_openai.acreate.return_value = mock_response

    response = await llm_module.validate_board(sample_board_data)
    
    # Verificaciones de la respuesta
    assert response.content is not None
    assert response.validation_results is not None
    assert response.validation_results.get("valid") is True
    assert response.metadata["response_type"] == ResponseType.VALIDATION.value

@pytest.mark.asyncio
async def test_suggestion_generation(llm_module, mock_openai):
    """
    Prueba la generación de sugerencias de mejora
    Verifica:
    1. La generación de múltiples sugerencias
    2. El formato correcto de las sugerencias
    3. La inclusión de metadatos apropiados
    """
    # Simula una respuesta con múltiples sugerencias
    suggestions_text = """
    - Implementar sistema de medición continua
    - Establecer reuniones diarias de seguimiento
    - Desarrollar plan de capacitación
    """
    mock_response = create_mock_completion(content=suggestions_text)
    mock_openai.acreate.return_value = mock_response

    # Contexto de ejemplo para las sugerencias
    context = {
        "current_state": "Proceso manual con tiempos variables",
        "target_state": "Proceso automatizado con tiempos consistentes"
    }
    
    response = await llm_module.generate_suggestions(context)
    
    # Verificaciones de las sugerencias generadas
    assert response.content is not None
    assert response.suggestions is not None
    assert len(response.suggestions) == 3
    assert response.metadata["response_type"] == ResponseType.SUGGESTION.value

@pytest.mark.asyncio
async def test_documentation_generation(llm_module, mock_openai):
    """
    Prueba la generación de documentación del proyecto
    Verifica:
    1. La generación correcta del formato del documento
    2. La inclusión de información del proyecto
    3. Los metadatos de la respuesta
    """
    # Simula una respuesta de documentación
    mock_response = create_mock_completion(
        content="# Reporte del Proyecto\n\nResumen ejecutivo..."
    )
    mock_openai.acreate.return_value = mock_response

    # Datos de ejemplo del proyecto
    project_data = {
        "title": "Mejora de Procesos 2024",
        "team": "Equipo Innovación",
        "results": {"kpi1": 95, "kpi2": 85}
    }
    
    response = await llm_module.generate_documentation(project_data)
    
    # Verificaciones del documento generado
    assert response.content is not None
    assert response.content.startswith("# Reporte")
    assert response.metadata["response_type"] == ResponseType.DOCUMENTATION.value

@pytest.mark.asyncio
async def test_temperature_handling(llm_module, mock_openai):
    """
    Prueba el manejo de la temperatura en las respuestas
    Verifica:
    1. El uso correcto de temperaturas personalizadas
    2. La inclusión de la temperatura en los metadatos
    """
    mock_response = create_mock_completion(content="Test response")
    mock_openai.acreate.return_value = mock_response

    # Crea una solicitud con temperatura personalizada
    request = LLMRequest(
        query="Test query",
        response_type=ResponseType.CHAT,
        temperature=0.8
    )
    
    response = await llm_module.process_request(request)
    
    # Verifica que se use la temperatura correcta
    assert response.metadata["temperature"] == 0.8

@pytest.mark.asyncio
async def test_error_handling(llm_module, mock_openai):
    mock_openai.acreate.side_effect = Exception("API Error")
    with pytest.raises(Exception):
        await llm_module.process_request(
            LLMRequest(query="Test query", response_type=ResponseType.CHAT)
        )

@pytest.mark.asyncio
async def test_complete_workflow(llm_module, mock_openai, sample_board_data):
    responses = [
        create_mock_completion('{"valid": true}'),
        create_mock_completion("- Sugerencia 1\n- Sugerencia 2"),
        create_mock_completion("# Documentación Final")
    ]
    mock_openai.acreate.side_effect = [
        AsyncMock(return_value=response) for response in responses
    ]