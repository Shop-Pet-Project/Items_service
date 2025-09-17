from typing import Annotated, AsyncIterator
from fastapi import Depends
from items_app.api.providers.repo_providers import get_item_repo, get_company_repo, get_user_repo
from items_app.api.providers.redis_providers import get_async_cache_manager
from items_app.application.items_applications.items_applications_service import (
    ItemsApplicationsService,
)
from items_app.application.companies_applications.companies_applications_service import (
    CompaniesApplicationsService,
)
from items_app.application.users_applications.users_cache_service import UserCacheService
from items_app.application.users_applications.users_applications_service import UsersApplicationsService
from items_app.application.auth_applications.auth_applications_service import AuthApplicationsService
from items_app.infrastructure.postgres.repositories.item_repo import ItemRepo
from items_app.infrastructure.postgres.repositories.company_repo import CompanyRepo
from items_app.infrastructure.postgres.repositories.user_repo import UserRepo
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager


# --- Получение сервисов для работы с сущностями ---

# --- Получение сервиса для работы с товарами ---
def get_items_app_service(
    item_repo: Annotated[ItemRepo, Depends(get_item_repo)],
    cache: Annotated[AsyncCacheManager, Depends(get_async_cache_manager)],
) -> ItemsApplicationsService:
    return ItemsApplicationsService(item_repo=item_repo, cache=cache)


# --- Получение сервиса для работы с компаниями ---
def get_companies_app_service(
    company_repo: Annotated[CompanyRepo, Depends(get_company_repo)],
    cache: Annotated[AsyncCacheManager, Depends(get_async_cache_manager)],
) -> CompaniesApplicationsService:
    return CompaniesApplicationsService(company_repo=company_repo, cache=cache)


# --- Получение сервиса для работы с пользователями ---
def get_users_cache_service(
    cache: Annotated[AsyncCacheManager, Depends(get_async_cache_manager)]
) -> UserCacheService:
    return UserCacheService(cache=cache)

def get_users_app_service(
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
    cache: Annotated[UserCacheService, Depends(get_users_cache_service)]
) -> UsersApplicationsService:
    return UsersApplicationsService(user_repo=user_repo, user_cache_service=cache)


# --- Получение сервиса для аутентификации ---
def get_auth_app_service(
    user_service: Annotated[UsersApplicationsService, Depends(get_users_app_service)]
) -> AuthApplicationsService:
    return AuthApplicationsService(user_service=user_service)
