from uuid import UUID
from typing import Optional, List
from items_app.infrastructure.redis.cache.async_cache_manager import AsyncCacheManager
from items_app.infrastructure.postgres.models import User


class UserCacheService:
    """
    Сервис для управления кешем пользователей.
    """

    def __init__(self, cache: AsyncCacheManager):
        self._cache = cache

    """
    Методы для сохранения кеша.
    1. set_user - сохраняет или обновляет одного пользователя.
    2. mset_users - сохраняет или обновляет несколько пользователей.
    3. set_all_users_list - сохраняет список всех пользователей с пагинацией.
    """

    async def set_user(self, user: User) -> None:
        """
        Сохраняет или обновляет пользователя в кеше.
        Сохраняет пользователя по двум ключам: по ID и по username.
        """
        cache_mapping = {
            self._cache.generate_key("user", user.id): user,
            self._cache.generate_key("user", user.username): user,
        }
        await self._cache.mset(mapping=cache_mapping)

    async def mset_users(self, users: List[User]) -> None:
        """
        Сохраняет или обновляет несколько пользователей в кеше.
        Сохраняет каждого пользователя по двум ключам: по ID и по username.
        """
        if not users:
            return
        cache_mapping = {}
        for user in users:
            cache_mapping[self._cache.generate_key("user", user.id)] = user
            cache_mapping[self._cache.generate_key("user", user.username)] = user
        await self._cache.mset(mapping=cache_mapping)

    async def set_all_users_list(
        self, users: List[User], offset: int, limit: int
    ) -> None:
        """Сохраняет список всех пользователей в кеше с пагинацией."""
        cache_key = self._cache.generate_key("users", offset, limit)
        await self._cache.set(cache_key, users)

    """
    Методы для получения кеша.
    1. get_user - получает одного пользователя по ID.
    2. mget_users - получает несколько пользователей по списку ID.
    3. get_all_users_list - получает список всех пользователей с пагинацией.
    """

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получает пользователя из кеша по ID."""
        cache_key = self._cache.generate_key("user", user_id)
        return await self._cache.get(cache_key)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Получает пользователя из кеша по username."""
        cache_key = self._cache.generate_key("user", username)
        return await self._cache.get(cache_key)

    async def mget_users_by_ids(self, user_ids: List[UUID]) -> List[Optional[User]]:
        """Получает несколько пользователей из кеша по списку ID."""
        cache_keys = [self._cache.generate_key("user", uid) for uid in user_ids]
        return await self._cache.mget(*cache_keys)

    async def get_all_users_list(self, offset: int, limit: int) -> Optional[List[User]]:
        """Получает список всех пользователей из кеша с пагинацией."""
        cache_key = self._cache.generate_key("users", offset, limit)
        return await self._cache.get(cache_key)

    """
    Метод для удаления кеша.
    1. delete_user - удаляет одного пользователя по ID.
    """

    async def delete_user_by_id(self, user_id: UUID):
        """Удаляет пользователя из кеша."""
        cache_key = self._cache.generate_key("user", user_id)
        await self._cache.delete(cache_key)

    """
    Методы для инвалидирования кеша.
    1. invalidate_all_users_list - инвалидирует все кешированные списки пользователей.
    2. invalidate_on_create - инвалидирует кеш при создании пользователя.
    3. invalidate_on_update - инвалидирует кеш при обновлении пользователя.
    4. invalidate_on_delete - инвалидирует кеш при удалении пользователя.
    """

    async def invalidate_all_users_list(self):
        """Инвалидирует все кешированные списки пользователей."""
        await self._cache.delete_pattern("users:*")

    async def invalidate_on_create(self):
        """Инвалидация кеша при создании нового пользователя."""
        await self.invalidate_all_users_list()

    async def invalidate_on_update(self, updated_user: User):
        """Инвалидация кеша при обновлении пользователя."""
        await self.set_user(updated_user)  # Обновляем кеш конкретного юзера
        await self.invalidate_all_users_list()  # Инвалидируем списки

    async def invalidate_on_delete(self, user_id: UUID):
        """Инвалидация кеша при удалении пользователя."""
        await self.delete_user_by_id(user_id)  # Удаляем кеш конкретного юзера
        await self.invalidate_all_users_list()  # Инвалидируем списки
