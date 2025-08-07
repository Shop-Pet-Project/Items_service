import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from items_app.main import app
from items_app.api.providers import get_session
from items_app.infrastructure.models import Base, Item


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_healthcheck(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == "Server is running"

@pytest.mark.asyncio
async def test_create_item(client):
    response = await client.post("/item", json={"title": "Candy", "price": 0.45})
    assert response.status_code == 200
    assert response.json() == {
        "message": "New item created successfully",
        "item": {
            "id": 1,
            "title": "Candy",
            "price": 0.45
        }
    }
