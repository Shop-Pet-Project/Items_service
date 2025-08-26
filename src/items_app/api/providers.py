from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from items_app.infrastructure.postgres.database import async_session
from items_app.infrastructure.postgres.repository import ItemRepo, CompanyRepo


async def get_session():
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


def get_item_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> ItemRepo:
    return ItemRepo(async_session=session)


def get_company_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompanyRepo:
    return CompanyRepo(async_session=session)
