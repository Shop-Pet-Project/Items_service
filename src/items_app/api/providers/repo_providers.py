from typing import Annotated, AsyncIterator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from items_app.api.providers.session_provider import get_session
from items_app.infrastructure.postgres.repositories.item_repo import ItemRepo
from items_app.infrastructure.postgres.repositories.company_repo import CompanyRepo
from items_app.infrastructure.postgres.repositories.user_repo import UserRepo


# --- Получение репозиториев для работы с БД ---
def get_item_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> ItemRepo:
    return ItemRepo(async_session=session)


def get_company_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompanyRepo:
    return CompanyRepo(async_session=session)


def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepo:
    return UserRepo(async_session=session)