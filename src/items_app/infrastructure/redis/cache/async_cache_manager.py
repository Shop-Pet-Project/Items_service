from typing import Any, Optional
from items_app.infrastructure.redis.cache.async_client import AsyncRedisClient
from items_app.infrastructure.redis.cache.base_serializer import BaseSerializer
from items_app.infrastructure.config import config


class AsyncCacheManager:
    def __init__(self, redis_client: AsyncRedisClient, serializer: BaseSerializer):
        self._redis = redis_client
        self._serializer = serializer

    def generate_key(self, *args: str) -> str:
        return ":".join(args)

    async def set(self, key: str, value: Any, ex: Optional[int] = config.REDIS_CACHE_EXPIRE_SECONDS) -> None:
        serialized_value = self._serializer.dumps(value)
        await self._redis.set(key, serialized_value, ex)

    async def get(self, key: str) -> Optional[Any]:
        cached_value = await self._redis.get(key)
        if cached_value is None:
            return None
        return self._serializer.loads(cached_value)

    async def delete(self, *keys: str) -> int:
        return await self._redis.delete(*keys)

    async def delete_pattern(self, pattern: str) -> int:
        keys_to_delete = []
        async for key in self._redis.scan_iter(match=pattern):
            keys_to_delete.append(key)
        return await self._redis.delete(*keys_to_delete) if keys_to_delete else 0