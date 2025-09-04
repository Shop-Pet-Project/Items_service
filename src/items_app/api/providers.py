from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from items_app.infrastructure.postgres.database import async_session
from items_app.infrastructure.postgres.repositories.item_repo import ItemRepo
from items_app.infrastructure.postgres.repositories.company_repo import CompanyRepo
from items_app.infrastructure.redis.cache.async_client import AsyncRedisClient
from items_app.infrastructure.redis.cache.json_serializer import JsonSerializer
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager
from items_app.application.items_applications.items_applications_service import (
    ItemsApplicationsService,
)
from items_app.application.companies_applications.companies_applications_service import (
    CompaniesApplicationsService,
)


# --- Получение сессии базы данных ---
async def get_session():
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


# --- Получение репозиториев для работы с БД ---
def get_item_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> ItemRepo:
    return ItemRepo(async_session=session)


def get_company_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompanyRepo:
    return CompanyRepo(async_session=session)


# --- Получение клиента Redis, сериализатора и менеджера кеша ---
def get_async_redis_client() -> AsyncRedisClient:
    return AsyncRedisClient()


def get_json_serializer() -> JsonSerializer:
    return JsonSerializer()


def get_async_cache_manager(
    redis_client: Annotated[AsyncRedisClient, Depends(get_async_redis_client)],
    json_serializer: Annotated[JsonSerializer, Depends(get_json_serializer)],
) -> AsyncCacheManager:
    return AsyncCacheManager(redis_client=redis_client, serializer=json_serializer)


# --- Получение сервисов для работы с сущностями ---
def get_items_app_service(
    item_repo: Annotated[ItemRepo, Depends(get_item_repo)],
    cache: Annotated[AsyncCacheManager, Depends(get_async_cache_manager)]
) -> ItemsApplicationsService:
    return ItemsApplicationsService(item_repo=item_repo, cache=cache)


def get_companies_app_service(
    company_repo: Annotated[CompanyRepo, Depends(get_company_repo)],
) -> CompaniesApplicationsService:
    return CompaniesApplicationsService(company_repo=company_repo)
