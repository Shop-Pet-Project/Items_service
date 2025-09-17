from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from items_app.api.providers.services_providers import get_auth_app_service
from items_app.application.auth_applications.auth_applications_service import (
    AuthApplicationsService,
)
from items_app.api.schemas.auth_schemas import UserCreateSchema, UserResponseSchema
from items_app.api.schemas.token_schemas import TokenSchema
from items_app.application.users_applications.users_applications_exceptions import (
    ConflictDataError,
)
from items_app.application.auth_applications.auth_applications_exceptions import (
    InvalidCredentialsError,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    summary="Регистрация нового пользователя",
    response_model=UserResponseSchema,
)
async def register_new_user(
    user_data: UserCreateSchema, 
    auth_service: Annotated[AuthApplicationsService, Depends(get_auth_app_service)]
):
    try:
        new_user = await auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )

        user_response = UserResponseSchema(
            id=new_user.id, username=new_user.username, email=new_user.email
        )
        return user_response
    except ConflictDataError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.post(
    "/login", summary="Аутентификация пользователя", response_model=TokenSchema
)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthApplicationsService, Depends(get_auth_app_service)]
):
    try:
        access_token_data = await auth_service.login_user_for_access_token(
            username=form_data.username, password=form_data.password
        )

        token_response = TokenSchema(**access_token_data)
        return token_response
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e
