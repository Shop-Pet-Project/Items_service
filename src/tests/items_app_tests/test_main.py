import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from items_app.main import app
from items_app.api.providers import get_session
from items_app.infrastructure.models import Base


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
    response = await client.get("/healthy")
    assert response.status_code == 200
    assert response.json() == "Server is running"


@pytest.mark.asyncio
async def test_create_item(client):
    response = await client.post("/items", json={"title": "Candy", "price": 0.45})
    assert response.status_code == 200
    assert response.json() == {
        "message": "New item created successfully",
        "item": {"id": 1, "title": "Candy", "price": 0.45},
    }


@pytest.mark.asyncio
async def test_get_item_by_id(client):
    response = await client.post("/items", json={"title": "Bombar", "price": 1.99})
    assert response.status_code == 200
    assert response.json() == {
        "message": "New item created successfully",
        "item": {"id": 2, "title": "Bombar", "price": 1.99},
    }

    response = await client.get("/items/2")
    assert response.status_code == 200
    assert response.json() == {"id": 2, "title": "Bombar", "price": 1.99}


@pytest.mark.asyncio
async def test_update_item_data_by_id(client):
    response = await client.post("/items", json={"title": "Cool Cola", "price": 1.45})
    assert response.status_code == 200
    assert response.json() == {
        "message": "New item created successfully",
        "item": {"id": 3, "title": "Cool Cola", "price": 1.45},
    }

    response = await client.get("/items/3")
    assert response.status_code == 200
    assert response.json() == {"id": 3, "title": "Cool Cola", "price": 1.45}

    response = await client.put("/items/3", json={"title": "Coca Cola", "price": 4.99})
    assert response.status_code == 200
    assert response.json() == {
        "message": "Item updated successfully",
        "item": {"id": 3, "title": "Coca Cola", "price": 4.99},
    }

    response = await client.get("/items/3")
    assert response.status_code == 200
    assert response.json() == {"id": 3, "title": "Coca Cola", "price": 4.99}


@pytest.mark.asyncio
async def test_delete_note_by_id(client):
    response = await client.get("/items/3")
    assert response.status_code == 200
    assert response.json() == {"id": 3, "title": "Coca Cola", "price": 4.99}

    response = await client.delete("/items/3")
    assert response.status_code == 200
    assert response.json() == {"message": "Item with item_id=3 was deleted"}

    response = await client.get("/items/3")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item with item_id=3 not found"}


@pytest.mark.asyncio
async def test_get_all_items(client):
    response = await client.get("/items")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "price": 0.45,
            "title": "Candy",
        },
        {
            "id": 2,
            "price": 1.99,
            "title": "Bombar",
        },
    ]


@pytest.mark.asyncio
async def test_get_all_items_with_empty_db(client):
    await client.delete("/items/1")
    await client.delete("/items/2")
    response = await client.get("/items")
    assert response.status_code == 200
    assert response.json() == {"message": "No items in database"}
