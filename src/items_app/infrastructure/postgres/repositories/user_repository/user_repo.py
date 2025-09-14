import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from items_app.infrastructure.postgres.models import User, Company
from items_app.infrastructure.postgres.repositories.user_repository.user_repo_exceptions import (
    UserHasCompaniesError,
)


logger = logging.getLogger(__name__)


class UserRepo:
    def __init__(self, async_session: AsyncSession):
        self._session = async_session

    async def add_user(self, user_data: User) -> Optional[User]:
        try:
            self._session.add(user_data)
            return user_data
        except SQLAlchemyError:
            await self._session.rollback()
            raise

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            stmt = select(User).where(User.id == user_id)
            cursor = await self._session.execute(stmt)
            result = cursor.scalar_one_or_none()
            return result
        except SQLAlchemyError:
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        try:
            stmt = select(User).where(User.username == username)
            cursor = await self._session.execute(stmt)
            result = cursor.scalar_one_or_none()
            return result
        except SQLAlchemyError:
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            stmt = select(User).where(User.email == email)
            cursor = await self._session.execute(stmt)
            result = cursor.scalar_one_or_none()
            return result
        except SQLAlchemyError:
            raise

    async def get_all_users(
        self, offset: Optional[int] = 0, limit: Optional[int] = 10
    ) -> Optional[List[User]]:
        try:
            stmt = select(User).offset(offset).limit(limit)
            cursor = await self._session.execute(stmt)
            result = list(cursor.scalars().all())
            return result or None
        except SQLAlchemyError:
            raise

    async def get_companies_own_by_user_by_id(
        self, user_id: UUID, offset: Optional[int] = 0, limit: Optional[int] = 10
    ) -> Optional[List[Company]]:
        try:
            stmt = (
                select(Company)
                .where(Company.user_id == user_id)
                .offset(offset)
                .limit(limit)
            )
            cursor = await self._session.execute(stmt)
            result = list(cursor.scalars().all())
            return result or None
        except SQLAlchemyError:
            raise

    async def update_user_data(self, update_data: User) -> Optional[User]:
        try:
            current_user = await self.get_user_by_id(update_data.id)
            if not current_user:
                return None
            current_user = update_data
            return current_user
        except SQLAlchemyError:
            await self._session.rollback()
            raise

    async def remove_user_by_id(self, user_id: UUID) -> Optional[bool]:
        try:
            current_user = await self.get_user_by_id(user_id)
            if not current_user:
                return None

            stmt = select(Company).where(Company.user_id == user_id)
            result = await self._session.execute(stmt)
            user_companies = result.scalars().all()

            if user_companies:
                raise UserHasCompaniesError(
                    user_id=user_id, companies=[c.name for c in user_companies]
                )

            await self._session.delete(current_user)
            return True

        except UserHasCompaniesError:
            raise
        except SQLAlchemyError:
            await self._session.rollback()
            raise

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except SQLAlchemyError:
            await self._session.rollback()
            raise

    async def rollback(self) -> None:
        await self._session.rollback()
