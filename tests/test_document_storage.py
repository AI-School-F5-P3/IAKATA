import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from pathlib import Path
from app.documentation.storage import DocumentStorage, Document, DocumentFormat  

@pytest.fixture
def mock_storage_handler():
    handler = DocumentStorage(base_dir=Path("./test_docs"))
    handler.Session = MagicMock()
    return handler

@pytest.fixture
def sample_document():
    return Document(
        id="doc_123",
        type="report",
        title="Sample Document",
        format=DocumentFormat.MARKDOWN,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"author": "Test User"},
        sections=[
            {"title": "Introduction", "content": "This is an intro.", "order": 1},
            {"title": "Conclusion", "content": "This is the end.", "order": 2}
        ]
    )

def test_save_document(mock_storage_handler, sample_document):
    with patch.object(mock_storage_handler, "_save_file", return_value=Path("/tmp/doc.md")):
        doc_id = pytest.run(mock_storage_handler.save_document(sample_document))
        assert doc_id == "doc_123"

def test_get_document(mock_storage_handler):
    session_mock = mock_storage_handler.Session.return_value
    session_mock.query.return_value.get.return_value = None  # Simular que no existe
    
    document = pytest.run(mock_storage_handler.get_document("doc_123"))
    assert document is None