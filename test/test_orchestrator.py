import pytest
from unittest.mock import Mock, AsyncMock
from app.orchestrator.orchestrator import RAGOrchestrator
from app.llm import LLMModule, LLMResponse, ResponseType
from app.retriever.search import SearchEngine
from app.retriever.types import SearchResult, RetrievedContext

# ====== FIXTURES ======

@pytest.fixture
def mock_llm():
    """Create a mock LLM module"""
    mock = Mock(spec=LLMModule)
    mock.process_request = AsyncMock(return_value=LLMResponse(
        content="Respuesta de prueba",
        metadata={"model": "gpt-4"}
    ))
    return mock

@pytest.fixture
def mock_search_engine():
    """Create a mock SearchEngine"""
    mock = Mock(spec=SearchEngine)
    mock.search = AsyncMock(return_value=SearchResult(
        query="test query",
        contexts=[
            RetrievedContext(
                content="Contexto de prueba",
                relevance_score=0.9,
                source="test_db"
            )
        ],
        total_results=1
    ))
    return mock

@pytest.fixture
def orchestrator(mock_llm, mock_search_engine):
    """Create RAGOrchestrator instance with mock components"""
    return RAGOrchestrator(
        llm=mock_llm,
        search_engine=mock_search_engine
    )

# ====== TEST CASES ======

@pytest.mark.asyncio
async def test_basic_query_processing(orchestrator):
    """Test basic query processing workflow"""
    response = await orchestrator.process_query(
        query="¿Cómo implementar Lean Kata?",
        response_type=ResponseType.CHAT
    )
    
    assert isinstance(response, LLMResponse)
    assert response.content is not None
    assert response.metadata is not None

@pytest.mark.asyncio
async def test_query_with_additional_context(orchestrator):
    """Test query processing with additional context"""
    additional_context = {
        "user_role": "manager",
        "project_type": "improvement"
    }
    
    response = await orchestrator.process_query(
        query="¿Cómo mejorar el proceso?",
        response_type=ResponseType.SUGGESTION,
        additional_context=additional_context
    )
    
    assert isinstance(response, LLMResponse)
    # Verify that the LLM was called with the combined context
    call_args = orchestrator.llm.process_request.call_args
    assert "user_role" in call_args[0][0].context

@pytest.mark.asyncio
async def test_error_handling(orchestrator, mock_search_engine):
    """Test error handling in orchestrator"""
    mock_search_engine.search.side_effect = Exception("Search failed")
    
    with pytest.raises(Exception):
        await orchestrator.process_query(
            query="test query",
            response_type=ResponseType.CHAT
        )

@pytest.mark.asyncio
async def test_different_response_types(orchestrator):
    """Test orchestrator with different response types"""
    for response_type in ResponseType:
        response = await orchestrator.process_query(
            query="test query",
            response_type=response_type
        )
        assert isinstance(response, LLMResponse)
        
@pytest.mark.asyncio
async def test_empty_query(orchestrator):
    """Test orchestrator behavior with empty query"""
    with pytest.raises(ValueError):
        await orchestrator.process_query(
            query="",
            response_type=ResponseType.CHAT
        )