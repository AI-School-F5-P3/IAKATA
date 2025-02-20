import pytest
from unittest.mock import AsyncMock
from app.api.main import get_data
import httpx

@pytest.mark.asyncio
async def test_get_data_success(monkeypatch):
    """
    Test para verificar que get_data retorna correctamente los datos de la API externa.
    """
    async def mock_get(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock()
        mock_response.json.return_value = {"id": 1, "name": "Challenge 1"}
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    data = await get_data()
    assert data["data"] == {"id": 1, "name": "Challenge 1"}

@pytest.mark.asyncio
async def test_get_data_http_error(monkeypatch):
    """
    Test para verificar que get_data maneje correctamente errores HTTP (por ejemplo, 404).
    """
    async def mock_get(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=kwargs.get("request"), response=mock_response
        )
        return mock_response

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    with pytest.raises(httpx.HTTPStatusError):
        await get_data()

@pytest.mark.asyncio
async def test_get_data_connection_error(monkeypatch):
    """
    Test para verificar que get_data maneje errores de conexión.
    """
    async def mock_get(*args, **kwargs):
        raise httpx.RequestError("Error de conexión")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    with pytest.raises(httpx.RequestError):
        await get_data()
