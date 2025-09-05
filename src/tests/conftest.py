import pytest_asyncio

class FakeRedisClient:
    def __init__(self):
        self._store = {}

    async def set(self, key, value, ex=None):
        self._store[key] = value

    async def get(self, key):
        return self._store.get(key)

    async def delete(self, *keys):
        count = 0
        for k in keys:
            if k in self._store:
                del self._store[k]
                count += 1
        return count

    def scan_iter(self, match="*"):
        for key in list(self._store.keys()):
            yield key

@pytest_asyncio.fixture(autouse=True)
async def mock_async_redis_client(monkeypatch):
    fake = FakeRedisClient()
    monkeypatch.setattr(
        "items_app.infrastructure.redis.cache.async_client.AsyncRedisClient",
        lambda: fake
    )
    yield
