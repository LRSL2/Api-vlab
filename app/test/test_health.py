import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db


@pytest.mark.asyncio
async def test_health_check_success(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert "database" in data
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_health_check_structure(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    required_fields = ["status", "version", "database"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_health_endpoint_database_status(client, db_session):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    assert "database" in data
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_health_check_version(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_check_with_db_error():
    from app.routers.health import health

    class BadDB:
        async def execute(self, *a, **k):
            raise RuntimeError("Connection failed")

    result = await health(db=BadDB())
    assert result["status"] == "ok"
    assert result["database"].startswith("error:")
    assert "Connection failed" in result["database"]


@pytest.mark.asyncio
async def test_health_endpoint_with_fake_db_error():
    async def fake_get_db_error():
        class FakeSession:
            async def execute(self, *a, **k):
                raise RuntimeError("DB error simulated")
        yield FakeSession()

    app.dependency_overrides[get_db] = fake_get_db_error
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
    app.dependency_overrides.pop(get_db, None)

    assert resp.status_code == 200
    data = resp.json()
    assert data["database"].startswith("error:")
