from datetime import timedelta
from typing import Optional, Dict
from items_app.application.auth_applications.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from items_app.application.auth_applications.auth_applications_exceptions import (
    InvalidUsernameError,
    InvalidPasswordError,
    InvalidCredentialsError,
)
from items_app.application.users_applications.users_applications_service import (
    UsersApplicationsService,
)
from items_app.application.users_applications.users_applications_exceptions import (
    ConflictDataError,
)
from items_app.infrastructure.postgres.models import User
from items_app.infrastructure.config import config


class AuthApplicationsService:
    def __init__(self, user_service: UsersApplicationsService):
        self._user_service = user_service

    async def register_user(self, username: str, email: str, password: str):
        """Регистрация нового пользователя."""
        try:
            # Хешируем пароль
            hashed_password = get_password_hash(password)

            # Создаем объект пользователя
            user_for_db = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
            )

            # Добавляем пользователя в базу данных
            new_user = await self._user_service.add_user(user_data=user_for_db)
            return new_user
        except ConflictDataError:
            # Пробрасываем ошибку конфликта данных, в случае если username или email уже заняты
            raise
        except Exception:
            raise

    async def authenticate_user(
        self, username: Optional[str], password: str
    ) -> Optional[User]:
        """Аутентификация пользователя по username и паролю."""
        user = await self._user_service.get_user_by_username(username)
        if not user:
            raise InvalidUsernameError(username)
        if not verify_password(password, user.hashed_password):
            raise InvalidPasswordError()
        return user

    async def login_user_for_access_token(
        self, username: str, password: str
    ) -> Dict[str, str]:
        """Аутентификация пользователя и возврат JWT токена."""
        try:
            user = await self.authenticate_user(username, password)

            access_token_expires = timedelta(
                minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )

            return {"access_token": access_token, "token_type": "bearer"}
        except InvalidCredentialsError:
            raise
        except Exception:
            raise
