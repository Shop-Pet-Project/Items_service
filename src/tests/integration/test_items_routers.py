import uuid

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
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_database():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


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
    data = response.json()
    assert data["message"] == "New item created successfully"

    item_id = data["item"]["id"]
    assert uuid.UUID(item_id).version == 4
    assert data["item"]["title"] == "Candy"
    assert data["item"]["price"] == 0.45


@pytest.mark.asyncio
async def test_get_item_by_id(client):
    create_resp = await client.post("/items", json={"title": "Bombar", "price": 1.99})
    item_id = create_resp.json()["item"]["id"]

    get_resp = await client.get(f"/items/{item_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == item_id
    assert data["title"] == "Bombar"
    assert data["price"] == 1.99


@pytest.mark.asyncio
async def test_update_item_data_by_id(client):
    create_resp = await client.post(
        "/items", json={"title": "Cool Cola", "price": 1.45}
    )
    item_id = create_resp.json()["item"]["id"]

    update_resp = await client.put(
        f"/items/{item_id}", json={"title": "Coca Cola", "price": 4.99}
    )
    assert update_resp.status_code == 200
    upd_data = update_resp.json()
    assert upd_data["item"]["title"] == "Coca Cola"
    assert upd_data["item"]["price"] == 4.99

    get_resp = await client.get(f"/items/{item_id}")
    assert get_resp.json()["title"] == "Coca Cola"


@pytest.mark.asyncio
async def test_delete_item_by_id(client):
    create_resp = await client.post("/items", json={"title": "Temp", "price": 1.0})
    item_id = create_resp.json()["item"]["id"]

    del_resp = await client.delete(f"/items/{item_id}")
    assert del_resp.status_code == 200
    assert f"{item_id}" in del_resp.json()["message"]

    get_resp = await client.get(f"/items/{item_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_all_items(client):
    await client.post("/items", json={"title": "Candy", "price": 0.45})
    await client.post("/items", json={"title": "Bombar", "price": 1.99})

    resp = await client.get("/items")
    assert resp.status_code == 200
    data = resp.json()
    titles = {item["title"] for item in data}
    assert {"Candy", "Bombar"} <= titles


@pytest.mark.asyncio
async def test_get_all_items_with_empty_db(client):
    resp = await client.get("/items")
    data = resp.json()
    assert data == {"message": "No items in database"}
