from typing import Annotated, AsyncIterator
from fastapi import Depends
from items_app.infrastructure.redis.cache.async_client import AsyncRedisClient
from items_app.infrastructure.redis.cache.json_serializer import JsonSerializer
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager


# --- Получение клиента Redis, сериализатора и менеджера кеша ---
async def get_async_redis_client() -> AsyncIterator[AsyncRedisClient]:
    client = AsyncRedisClient()
    try:
        yield client
    finally:
        await client.close()


def get_json_serializer() -> JsonSerializer:
    return JsonSerializer()


def get_async_cache_manager(
    redis_client: Annotated[AsyncRedisClient, Depends(get_async_redis_client)],
    json_serializer: Annotated[JsonSerializer, Depends(get_json_serializer)],
) -> AsyncCacheManager:
    return AsyncCacheManager(redis_client=redis_client, serializer=json_serializer)
