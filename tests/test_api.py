import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_ticket():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/tickets",
            json={
                "subject": "Test ticket",
                "content": "This is a test",
                "source": "test"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["subject"] == "Test ticket"

@pytest.mark.asyncio
async def test_list_tickets():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/tickets")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_metrics():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_tickets" in data
        assert "automation_rate" in data