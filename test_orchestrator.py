import pytest
from unittest.mock import Mock, AsyncMock
from app.llm.types import ResponseType, LLMRequest, LLMResponse
from app.vectorstore.common_types import TextType, ProcessedText
from app.orchestrator.orchestrator import RAGOrchestrator

@pytest.fixture
def mock_vector_store():
    mock = Mock()
    mock.hybrid_search = AsyncMock(return_value=[
        {
            'id': 'doc1',
            'text': 'Este es un texto de prueba sobre Lean Kata',
            'score': 0.8,
            'metadata': {
                'section_id': 'section1',
                'type': 'main_content',
                'title': 'Introducción a Lean Kata'
            }
        },
        {
            'id': 'doc2',
            'text': 'Toyota Kata es una metodología de mejora continua',
            'score': 0.7,
            'metadata': {
                'section_id': 'section2',
                'type': 'example',
                'title': 'Ejemplos de Kata'
            }
        }
    ])
    return mock

@pytest.fixture
def mock_llm():
    mock = Mock()
    mock.process_request = AsyncMock(return_value=LLMResponse(
        content="Toyota Kata es una metodología que ayuda a las organizaciones a mejorar continuamente",
        metadata={
            "model": "gpt-4",
            "tokens": 150
        },
        confidence=0.9
    ))
    mock.validation_criteria = {
        'validation': {
            'specific': 'específico',
            'relevant': 'relevante',
            'measurable': 'medible'
        }
    }
    return mock

@pytest.fixture
def mock_validator():
    mock = Mock()
    mock.process_validation = Mock(return_value={
        'valid': True,
        'specific': True,
        'relevant': True
    })
    return mock

@pytest.fixture
def orchestrator(mock_vector_store, mock_llm, mock_validator):
    return RAGOrchestrator(
        vector_store=mock_vector_store,
        llm=mock_llm,
        validator=mock_validator
    )

@pytest.mark.asyncio
async def test_process_query_basic_flow(orchestrator):
    """Prueba el flujo básico del procesamiento de consultas"""
    query = "¿Qué es Lean Kata?"
    response = await orchestrator.process_query(
        query=query,
        response_type=ResponseType.CHAT
    )
    
    # Verificar que se llamó a hybrid_search
    orchestrator.vector_store.hybrid_search.assert_called_once()
    
    # Verificar que se llamó a process_request del LLM
    orchestrator.llm.process_request.assert_called_once()
    
    # Verificar la estructura de la respuesta
    assert response.content is not None
    assert response.metadata is not None
    assert 'sources' in response.metadata
    assert len(response.metadata['sources']) == 2
    assert response.confidence is not None

@pytest.mark.asyncio
async def test_process_query_with_validation(orchestrator):
    """Prueba el procesamiento de consultas con validación"""
    query = "Valida este experimento Kata"
    response = await orchestrator.process_query(
        query=query,
        response_type=ResponseType.VALIDATION
    )
    
    # Verificar que se realizó la validación
    assert 'validation' in response.metadata
    assert response.metadata['validation']['valid'] is True
    
    # Verificar que se usaron los criterios de validación
    orchestrator.validator.process_validation.assert_called_once()

@pytest.mark.asyncio
async def test_process_query_with_custom_params(orchestrator):
    """Prueba el procesamiento con parámetros personalizados"""
    query = "¿Cómo implementar Lean Kata?"
    response = await orchestrator.process_query(
        query=query,
        response_type=ResponseType.CHAT,
        top_k=3,
        temperature=0.7,
        language="es"
    )
    
    # Verificar que se pasaron los parámetros correctamente
    assert orchestrator.vector_store.hybrid_search.call_args[1]['top_k'] == 3
    
    llm_request = orchestrator.llm.process_request.call_args[0][0]
    assert isinstance(llm_request, LLMRequest)
    assert llm_request.temperature == 0.7
    assert llm_request.language == "es"

@pytest.mark.asyncio
async def test_process_query_context_building(orchestrator):
    """Prueba la construcción del contexto"""
    query = "¿Qué es Lean Kata?"
    response = await orchestrator.process_query(
        query=query,
        response_type=ResponseType.CHAT
    )
    
    # Verificar la estructura del contexto en la llamada al LLM
    llm_request = orchestrator.llm.process_request.call_args[0][0]
    assert 'relevant_texts' in llm_request.context
    assert 'metadata' in llm_request.context
    
    # Verificar que los textos relevantes están presentes
    relevant_texts = llm_request.context['relevant_texts']
    assert len(relevant_texts) > 0
    assert all('text' in text and 'score' in text for text in relevant_texts)

@pytest.mark.asyncio
async def test_process_query_error_handling(orchestrator, mock_vector_store):
    """Prueba el manejo de errores"""
    # Simular un error en la búsqueda
    mock_vector_store.hybrid_search.side_effect = Exception("Error de búsqueda")
    
    with pytest.raises(Exception) as exc_info:
        await orchestrator.process_query(
            query="¿Qué es Lean Kata?",
            response_type=ResponseType.CHAT
        )
    
    assert "Error en el orquestador RAG" in str(exc_info.value)

def test_orchestrator_initialization(mock_vector_store, mock_llm, mock_validator):
    """Prueba la inicialización del orquestador"""
    orchestrator = RAGOrchestrator(mock_vector_store, mock_llm, mock_validator)
    
    assert orchestrator.vector_store == mock_vector_store
    assert orchestrator.llm == mock_llm
    assert orchestrator.validator == mock_validator
    assert orchestrator.context_window > 0  # Verifica que se estableció un tamaño de ventana