import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient

from items_app.main import app
from items_app.api.providers import get_session
from items_app.infrastructure.postgres.models import Base
from items_app.infrastructure.redis.cache.async_client import AsyncRedisClient

# --- Настройка тестовой базы ---
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


# --- Фикстура для инициализации тестовой БД ---
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# --- Переопределение зависимости get_session ---
async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


# --- Фикстура отчисти БД и кеша перед каждым тестом ---
@pytest_asyncio.fixture(autouse=True, scope="function")
async def cleanup_database():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    redis_client = AsyncRedisClient()
    async for key in redis_client.scan_iter("*"):
        await redis_client.delete(key)

    yield


# --- Фикстура создающая клиента для запросов
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
