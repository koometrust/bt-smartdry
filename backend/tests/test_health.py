import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["ml_models_loaded"] is True
    assert "sms_provider_mode" in data
    assert data["sms_provider_mode"] in ["mock", "sandbox", "live"]
