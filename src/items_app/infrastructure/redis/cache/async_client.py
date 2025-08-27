from typing import Optional, AsyncIterator
from redis.asyncio import Redis as AsyncRedis
from items_app.infrastructure.config import config


class AsyncRedisClient:
    def __init__(self):
        self._client = AsyncRedis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
        )

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        await self._client.set(name=key, value=value, ex=ex)

    async def get(self, key: str) -> Optional[str]:
        return await self._client.get(name=key)

    async def delete(self, *keys: str) -> int:
        return await self._client.delete(*keys)

    def scan_iter(self, match: str) -> AsyncIterator[str]:
        return self._client.scan_iter(match=match)
