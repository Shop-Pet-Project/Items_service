from typing import List, Dict, Any, Optional
from items_app.infrastructure.redis.cache.async_client import AsyncRedisClient
from items_app.infrastructure.redis.cache.base_serializer import BaseSerializer
from items_app.infrastructure.config import config


class AsyncCacheManager:
    def __init__(self, redis_client: AsyncRedisClient, serializer: BaseSerializer):
        self._redis = redis_client
        self._serializer = serializer

    def generate_key(self, *args: Any) -> str:
        return ":".join(str(arg) for arg in args)

    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = config.REDIS_CACHE_EXPIRE_SECONDS,
    ) -> None:
        serialized_value = self._serializer.dumps(value)
        await self._redis.set(key, serialized_value, ex)

    async def mset(
        self,
        mapping: Dict[str, Any],
        ex: Optional[int] = config.REDIS_CACHE_EXPIRE_SECONDS,
    ) -> None:
        serialized_mapping = {
            key: self._serializer.dumps(value) for key, value in mapping.items()
        }
        await self._redis.mset(serialized_mapping)

    async def get(self, key: str) -> Optional[Any]:
        cached_value = await self._redis.get(key)
        if cached_value is None:
            return None
        return self._serializer.loads(cached_value)

    async def mget(self, *keys: str) -> List[Optional[Any]]:
        cached_values = await self._redis.mget(*keys)
        return [
            self._serializer.loads(value) if value is not None else None
            for value in cached_values
        ]

    async def delete(self, *keys: str) -> int:
        return await self._redis.delete(*keys)

    async def delete_pattern(self, *patterns: str) -> int:
        keys_to_delete = []
        for pattern in patterns:
            matching_keys = self._redis.scan_iter(match=pattern)
            async for key in matching_keys:
                keys_to_delete.append(key)
        return await self._redis.delete(*keys_to_delete) if keys_to_delete else 0
