from fastapi import APIRouter, Depends
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager
from items_app.api.providers.redis_providers import get_async_cache_manager


router = APIRouter(prefix="/healthy", tags=["Healthcheck"])


@router.get("", summary="Проверка работы приложения")
async def healthcheck():
    return {"status": "ok"}


@router.get("/ping-cache", summary="Проверка работы кеша Redis")
async def ping_cache(cache: AsyncCacheManager = Depends(get_async_cache_manager)):
    key = cache.generate_key("ping", "test")
    await cache.set(key, {"status": "ok"})
    return await cache.get(key)
