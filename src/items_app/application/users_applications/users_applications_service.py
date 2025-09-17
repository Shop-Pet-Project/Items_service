import logging
from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError
from items_app.application.users_applications.users_cache_service import (
    UserCacheService,
)
from items_app.infrastructure.postgres.models import User
from items_app.infrastructure.postgres.repositories.user_repo import UserRepo
from items_app.application.users_applications.users_applications_exceptions import (
    UsernameAlreadyExistError,
    EmailAlreadyExistError,
    UserNotFoundError,
    UserHasCompaniesError,
    ForbiddenError,
    AccessToAnotherUserError,
)


logger = logging.getLogger(__name__)


@dataclass
class MultipleUsersResponse:
    """Датакласс для результата получения нескольких пользователей."""

    found_users: List[User]
    missing_user_ids: List[UUID]


class UsersApplicationsService:
    """
    Сервис для работы с пользователями.
    Реализует логику добавления, получения, обновления и удаления пользователей.
    """

    def __init__(self, user_repo: UserRepo, cache: UserCacheService):
        self._user_repo = user_repo
        self._cache = cache

    async def add_user(self, user_data: User) -> Optional[User]:
        """Добавление нового пользователя в БД при условии уникальности username и email."""
        try:
            # 1. Проверка на уникальность username и email
            existing_user_by_username = self._user_repo.get_user_by_username(
                user_data.username
            )
            if existing_user_by_username:
                raise UsernameAlreadyExistError(user_data.username)
            existing_user_by_email = self._user_repo.get_user_by_email(user_data.email)
            if existing_user_by_email:
                raise EmailAlreadyExistError(user_data.email)

            # 2. Если user_data прошла проверку на уникальность, добавляем в БД
            new_user = self._user_repo.add_user(user_data)
            await self._user_repo.commit()

            # 3. ИНВАЛИДАЦИЯ: очищаем кеш со списком всех пользователей
            await self._cache.invalidate_on_create()

            # 4. Возврат результата
            return new_user
        except SQLAlchemyError as e:
            await self._user_repo.rollback()
            logger.error(f"Database error adding user: {e}")
            raise
        except Exception as e:
            self._user_repo.rollback()
            logger.error(f"Error adding user: {e}")
            raise

    async def get_user_by_id(self, user_id: UUID, current_user: User) -> Optional[User]:
        """Получение пользователя по ID с проверкой прав доступа."""
        try:
            # 1. Проверка прав доступа
            if current_user.role != "admin" and current_user.id != user_id:
                raise AccessToAnotherUserError(target_user_id=user_id)

            # 2. Попытка получить данные из кеша
            if cache_value := await self._cache.get_user_by_id(user_id):
                return cache_value

            # 3. Если данных нет в кеше, идем в базу данных
            user = await self._user_repo.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(user_id)

            # 4. Кеширование полученных данных
            await self._cache.set_user(user)

            # 5. Возврат результата
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user by id: {e}")
            raise
        except Exception as e:
            await self._user_repo.rollback()
            logger.error(f"Error while fetching user by id: {e}")
            raise

    async def get_multiple_users_by_ids(
        self, user_ids: List[UUID], current_user: User
    ) -> MultipleUsersResponse:
        """Получение нескольких пользователей по списку ID с проверкой прав доступа."""
        try:
            # 1. Проверка прав доступа
            if current_user.role != "admin":
                raise ForbiddenError()

            # 2. Убираем дубликаты для эффективности
            unique_user_ids = list(set(user_ids))

            # 3. Пытаемся получить всех из кеша
            cached_users_data = await self._cache.mget_users_by_ids(unique_user_ids)

            # 3.1. Отфильтровываем найденных в кеше пользователей
            found_users = [data for data in cached_users_data if data is not None]
            found_user_ids = {user.id for user in found_users}

            # 4. Определяем, какие ID еще нужно найти в базе данных
            ids_to_fetch_from_db = [
                uid for uid in unique_user_ids if uid not in found_user_ids
            ]

            # 5. Если остались ID для поиска, идем в базу
            if ids_to_fetch_from_db:
                db_users = await self._user_repo.get_several_users_by_ids(
                    ids_to_fetch_from_db
                )

                # 6. Кешируем новых пользователей и добавляем их в общий список
                if db_users:
                    users_to_cache = []
                    for user in db_users:
                        users_to_cache.append(user)
                        found_users.append(user)

                    if users_to_cache:
                        await self._cache.mset_users(users_to_cache)

            # 7. Собираем итоговый результат
            final_found_ids = {user.id for user in found_users}
            missing_user_ids = [
                uid for uid in unique_user_ids if uid not in final_found_ids
            ]

            # 8. Возврат результата
            return MultipleUsersResponse(
                found_users=found_users, missing_user_ids=missing_user_ids
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching multiple users by ids: {e}")
            raise
        except Exception as e:
            logger.error(f"Error while fetching multiple users by ids: {e}")
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Получение пользователя по username для аутентификации без проверки прав доступа.
        В случае если пользователь не найден, возвращается None.
        Исключение UserNotFoundError не выбрасывается, чтобы AuthApplicationsService мог обработать ситуацию самостоятельно.
        """
        try:
            # 1. Попытка получить данные из кеша
            if cache_value := await self._cache.get_user_by_username(username):
                return cache_value

            # 2. Если данных нет в кеше, идем в базу данных
            user = await self._user_repo.get_user_by_username(username)
            if not user:
                return None

            # 3. Кеширование полученных данных
            await self._cache.set_user(user)

            # 4. Возврат результата
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user by username: {e}")
            raise
        except Exception as e:
            logger.error(f"Error while fetching user bu username: {e}")
            raise

    async def get_all_users(
        self, current_user: User, offset: Optional[int] = 0, limit: Optional[int] = 10
    ) -> List[Optional[User]]:
        """Получение всех пользователей с пагинацией и проверкой прав доступа."""
        try:
            # 1. Проверка прав доступа
            if current_user.role != "admin":
                raise ForbiddenError()

            # 2. Попытка получить данные из кеша
            if cache_value := await self._cache.get_all_users_list(offset, limit):
                return cache_value

            # 3. Если данных нет в кеше, идем в базу данных
            users = await self._user_repo.get_all_users(offset, limit)
            if not users:
                return []

            # 4. Кеширование полученных данных
            await self._cache.set_all_users_list(users, offset, limit)

            # 5. Возврат результата
            return users
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching all users: {e}")
            raise
        except Exception as e:
            logger.error(f"Error while fetching all users: {e}")
            raise

    async def update_user(
        self, update_data: User, current_user: User
    ) -> Optional[User]:
        """Обновление данных пользователя с проверкой прав доступа и уникальности username/email."""
        try:
            # 1. Проверка прав доступа
            if current_user.role != "admin" and current_user.id != update_data.id:
                raise AccessToAnotherUserError(target_user_id=update_data.id)

            # 2. Проверка существования пользователя
            existing_user = await self._user_repo.get_user_by_id(update_data.id)
            if not existing_user:
                raise UserNotFoundError(update_data.id)

            # 3. Проверка уникальности username и email при их изменении
            if update_data.username != existing_user.username:
                user_with_same_username = await self._user_repo.get_user_by_username(
                    update_data.username
                )
                if user_with_same_username:
                    raise UsernameAlreadyExistError(update_data.username)

            if update_data.email != existing_user.email:
                user_with_same_email = await self._user_repo.get_user_by_email(
                    update_data.email
                )
                if user_with_same_email:
                    raise EmailAlreadyExistError(update_data.email)

            # 4. Обновление данных в базе данных
            updated_user = await self._user_repo.update_user_data(update_data)
            await self._user_repo.commit()

            # 5. ИНВАЛИДАЦИЯ: очистка всех списков пользователей и обновление кеша конкретного пользователя
            await self._cache.invalidate_on_update(updated_user)

            # 6. Возврат результата
            return updated_user
        except SQLAlchemyError as e:
            await self._user_repo.rollback()
            logger.error(f"Database error updating user: {e}")
            raise
        except Exception as e:
            await self._user_repo.rollback()
            logger.error(f"Error updating user: {e}")
            raise

    async def delete_user(self, user_id: UUID, current_user: User) -> None:
        """Удаление пользователя с проверкой прав доступа и наличия связанных компаний."""
        try:
            # 1. Проверка прав доступа
            if current_user.role != "admin" and current_user.id != user_id:
                raise AccessToAnotherUserError(target_user_id=user_id)

            # 2. Проверка существования пользователя
            # Если пользователь есть в кеше, берем оттуда, иначе из базы
            if cache_value := await self._cache.get_user_by_id(user_id):
                user_to_delete = cache_value
            else:
                user_to_delete = await self._user_repo.get_user_by_id(user_id)
                if not user_to_delete:
                    raise UserNotFoundError(user_id)

            # 3. Проверка наличия связанных компаний
            # Нельзя удалять пользователя, если у него есть связанные компании
            user_companies = await self._user_repo.get_user_companies_by_id(user_id)
            if user_companies:
                raise UserHasCompaniesError(user_id)

            # 4. Удаление пользователя из базы данных
            await self._user_repo.remove_user_by_id(user_id)
            await self._user_repo.commit()

            # 5. ИНВАЛИДАЦИЯ: удаление кеша конкретного пользователя и очистка всех списков пользователей
            await self._cache.invalidate_on_delete(user_id)

            # 6. Возврат результата (ничего не возвращаем)
            return
        except SQLAlchemyError as e:
            await self._user_repo.rollback()
            logger.error(f"Database error deleting user: {e}")
            raise
        except Exception as e:
            await self._user_repo.rollback()
            logger.error(f"Error deleting user: {e}")
            raise
