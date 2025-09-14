import logging
from uuid import UUID
from typing import Optional, List
from items_app.application.users_applications.users_applications_exceptions import (
    UsernameAlreadyExistError,
    EmailAlreadyExistError,
    UserIdNotFoundError,
    NoAccessRightsError,
    AccessAnotherUserDataError,
)
from items_app.infrastructure.postgres.repositories.user_repository.user_repo import (
    UserRepo,
)
from items_app.infrastructure.postgres.repositories.user_repository.user_repo_exceptions import (
    UserHasCompaniesError,
)
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager
from items_app.infrastructure.postgres.models import User


logger = logging.getLogger(__name__)


class UsersApplicationsService:
    def __init__(self, user_repo: UserRepo, cache: AsyncCacheManager):
        self.user_repo = user_repo
        self.cache = cache

    async def create_user(self, user_data: User) -> Optional[User]:
        try:
            # Проверка, существует ли такие username и email в БД
            is_username_exist = await self.user_repo.get_user_by_username(
                username=user_data.username
            )
            if is_username_exist:
                raise UsernameAlreadyExistError(username=user_data.username)
            is_email_exist = await self.user_repo.get_user_by_email(
                email=user_data.email
            )
            if is_email_exist:
                raise EmailAlreadyExistError(email=user_data.email)

            new_user = await self.user_repo.add_user(user_data=user_data)
            await self.user_repo.commit()
            return new_user
        except Exception as e:
            await self.user_repo.rollback()
            logger.error(f"Error of creating user: {e}")
            raise

    async def fetch_user_by_id(
        self, user_id: UUID, current_user: User
    ) -> Optional[User]:
        try:
            if current_user.role != "admin" and user_id != current_user.id:
                raise NoAccessRightsError()

            response = await self.user_repo.get_user_by_id(user_id=user_id)
            if not response:
                raise UserIdNotFoundError(user_id=user_id)
            return response
        except Exception as e:
            logger.error(f"Error of fetching user by id: {e}")
            raise

    async def fetch_all_users(
        self, current_user: User, offset: Optional[int] = 0, limit: Optional[int] = 10
    ) -> List[User]:
        try:
            if current_user.role != "admin":
                raise NoAccessRightsError()

            response = await self.user_repo.get_all_users(offset=offset, limit=limit)
            return response or []
        except Exception as e:
            logger.error(f"Error of fetching all users: {e}")
            raise

    async def update_user_data(
        self, update_data: User, current_user: User
    ) -> Optional[User]:
        try:
            if current_user.role != "admin" and update_data.id != current_user.id:
                raise AccessAnotherUserDataError(user_id=update_data.id)

            user_response = await self.user_repo.update_user_data(
                update_data=update_data
            )
            if not user_response:
                raise UserIdNotFoundError(user_id=update_data.id)
            await self.user_repo.commit()
            return user_response
        except Exception as e:
            await self.user_repo.rollback()
            logger.error(f"Error of updating data of user: {e}")
            raise

    async def delete_user_by_id(
        self, user_id: UUID, current_user: User
    ) -> Optional[bool]:
        try:
            if current_user.role != "admin" and user_id != current_user.id:
                raise AccessAnotherUserDataError(user_id=user_id)

            response = await self.user_repo.remove_user_by_id(user_id=user_id)
            return response
        except UserHasCompaniesError as e:
            await self.user_repo.rollback()
            raise
        except Exception as e:
            await self.user_repo.rollback()
            logger.error(f"Error of deleting user: {e}")
            raise
