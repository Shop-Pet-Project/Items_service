from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from items_app.api.providers.services_providers import get_users_app_service
from items_app.application.users_applications.users_applications_service import UsersApplicationsService
from items_app.infrastructure.postgres.models import User
from items_app.infrastructure.config import config



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# --- Получение текущего пользователя из токена ---
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    user_service: Annotated[UsersApplicationsService, Depends(get_users_app_service)]
) -> User:
    """Получение текущего пользователя из JWT токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_username(username=username)
    if not user:
        raise credentials_exception
    return user
