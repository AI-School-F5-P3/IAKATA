import pytest
from unittest.mock import Mock, AsyncMock
from app.retriever.types import SearchQuery, SearchResult, RetrievedContext
from app.retriever.search import SearchEngine

# ====== FIXTURES ======

@pytest.fixture
def search_engine():
    """Create a SearchEngine instance for testing"""
    return SearchEngine()

@pytest.fixture
def sample_query():
    """Create a sample search query"""
    return SearchQuery(
        query="¿Cómo mejorar el tiempo de ciclo?",
        filters={"type": "lean_kata"},
        top_k=3
    )

# ====== TEST CASES ======

@pytest.mark.asyncio
async def test_basic_search(search_engine, sample_query):
    """Test basic search functionality"""
    result = await search_engine.search(sample_query)
    
    assert isinstance(result, SearchResult)
    assert result.query == sample_query.query
    assert len(result.contexts) > 0
    assert isinstance(result.contexts[0], RetrievedContext)
    assert result.total_results > 0

@pytest.mark.asyncio
async def test_search_with_empty_query(search_engine):
    """Test search behavior with empty query"""
    empty_query = SearchQuery(query="", top_k=3)
    
    with pytest.raises(ValueError):
        await search_engine.search(empty_query)

@pytest.mark.asyncio
async def test_search_with_invalid_top_k(search_engine):
    """Test search behavior with invalid top_k value"""
    invalid_query = SearchQuery(query="test", top_k=-1)
    
    with pytest.raises(ValueError):
        await search_engine.search(invalid_query)