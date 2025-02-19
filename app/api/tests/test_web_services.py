from fastapi.testclient import TestClient
from app.api.main import app
from app.api.models import FormData
import pytest
import json
from pathlib import Path

client = TestClient(app)

def test_generate_response_success():
    """Test para verificar una respuesta exitosa del endpoint /board/ai"""
    test_payload = {
        "id": "R123",  # Añadido id que ahora es requerido
        "userId": 1,   # Añadido userId que ahora es requerido
        "description": "This is a test description",
        "name": "Test Name"  # Opcional pero incluido para completitud
    }
    
    response = client.post(
        "/board/ai",
        json=test_payload
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "message" in response.json()
    assert "data" in response.json()
    
    data_response = response.json()["data"]
    assert "description" in data_response
    assert "sugerencia:" in data_response["description"]

def test_generate_response_missing_required_fields():
    """Test para verificar el manejo de campos faltantes requeridos"""
    # Test sin description
    response = client.post(
        "/board/ai",
        json={
            "id": "R123",
            "userId": 1
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    
    # Test sin id
    response = client.post(
        "/board/ai",
        json={
            "userId": 1,
            "description": "Test description"
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    
    # Test sin userId
    response = client.post(
        "/board/ai",
        json={
            "id": "R123",
            "description": "Test description"
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()

def test_generate_response_invalid_data():
    """Test para verificar el manejo de datos inválidos"""
    response = client.post(
        "/board/ai",
        json={
            "id": 123,  # Tipo incorrecto (debe ser string)
            "userId": "invalid",  # Tipo incorrecto (debe ser int)
            "description": None  # Tipo incorrecto (debe ser string)
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Fixture para configurar el ambiente de pruebas"""
    # Aquí podrías agregar cualquier configuración necesaria
    # Por ejemplo, asegurarte de que los vectores están cargados
    vectors_dir = Path(__file__).parent.parent / "vectorstore" / "processed" / "vectors"
    assert vectors_dir.exists(), f"Directory {vectors_dir} does not exist"
    required_files = ["faiss.index", "metadata.npy", "chunk_data.json"]
    for file in required_files:
        assert (vectors_dir / file).exists(), f"Required file {file} not found in {vectors_dir}"
    yield