from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_generate_response_success():
    response = client.post(
        "/board/ai",
        json={"description": "This is a test description"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    data_response = response.json()["data"]
    assert "sugerencia: This is a test description" in data_response["description"]

def test_generate_response_missing_description():
    response = client.post(
        "/board/ai",
        json={"project_name": "Test Project"}
    )
    assert response.status_code == 422  # Unprocessable Entity (faltan datos)
    assert "detail" in response.json()

