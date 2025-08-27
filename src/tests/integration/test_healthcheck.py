import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from items_app.main import app
from items_app.api.providers import get_session
from items_app.infrastructure.postgres.models import Base
from tests.integration.conftest import TestingSessionLocal, engine, setup_database  # noqa: F401


# --- Переопределение зависимости для использования тестовой БД ---
async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


# --- Фикстуры ---
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# --- Тесты ---
@pytest.mark.asyncio
async def test_healthcheck(client: AsyncClient):
    resp = await client.get("/healthy")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


# @pytest.mark.asyncio
# async def test_ping_cache(client: AsyncClient):
#     resp = await client.get("/healthy/ping-cache")
#     assert resp.status_code == 200
#     data = resp.json()
#     assert data["status"] == "ok"
