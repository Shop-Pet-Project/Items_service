from uuid import UUID
from typing import Union, List


class UserApplicationsError(Exception):
    """
    Базовый класс исключений, связанных с пользовательским сервисом.
    """
    pass


# --- Ошибки конфликта данных ---

class ConflictDataError(UserApplicationsError):
    """
    Базовый класс исключений, связанных с конфликтом данных.
    """
    pass


class UsernameAlreadyExistError(ConflictDataError):
    """
    Исключение, выбрасываемое при попытке создании нового пользователя,
    в случае если его username уже есть в БД.

    Args:
        username (str): Username пользователя.
    """

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User with username {self.username} already exist")


class EmailAlreadyExistError(ConflictDataError):
    """
    Исключение, выбрасываемое при попытке создании нового пользователя,
    в случае если его email уже есть в БД.

    Args:
        email (str): Email пользователя.
    """

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {self.email} already exist")


# --- Ошибки поиска данных ---

class NotFoundError(UserApplicationsError):
    """
    Базовый класс исключений, связанных с отсутствием данных.
    """
    pass


class UserNotFoundError(NotFoundError):
    """
    Исключение, выбрасываемое при попытке получить данные несуществуюшего пользователя.

    Args:
        user_id (UUID): ID пользователя.
    """

    def __init__(self, user_ids: Union[UUID, List[UUID]]):
        self.user_ids = user_ids
        
        if isinstance(user_ids, list):
            # Если передан список ID
            ids_str = ", ".join(f"'{str(uid)}'" for uid in user_ids)
            message = f"Users with IDs {ids_str} not found"
        else:
            # Если передан один ID
            message = f"User with ID '{user_ids}' not found"
            
        super().__init__(message)


# --- Ошибки бизнес логики ---

class BusinessLogicError(UserApplicationsError):
    """
    Базовый класс исключений, связанных с ошибками бизнес логики.
    """
    pass


class UserHasCompaniesError(BusinessLogicError):
    """
    Исключение, выбрасываемое при попытке удалить пользователя,
    у которого есть связанные компании.

    Args:
        user_id (UUID): ID пользователя.
        companies (List[str]): Список названий компаний, связанных с пользователем.
    """

    def __init__(self, user_id: UUID, companies: list[str]):
        self.user_id = user_id
        self.companies = companies
        companies_str = ", ".join(self.companies)
        super().__init__(
            f"Cannot delete user with id {self.user_id} because they have associated companies: {companies_str}"
        )


# --- Ошибки доступа ---

class AccessError(UserApplicationsError):
    """
    Базовый класс исключений, связанных с ошибками доступа.
    """
    pass


class ForbiddenError(AccessError):
    """
    Исключение, выбрасываемое при попытке доступа к ресурсу,
    на который у пользователя нет прав доступа.
    """
    
    def __init__(self, message: str = "Access denied. You do not have permission to access this resource."):
        super().__init__(message)


class AccessToAnotherUserError(AccessError):
    """
    Исключение, выбрасываемое при попытке доступа к данным другого пользователя.
    """
    
    def __init__(self, target_user_id: UUID):
        self.target_user_id = target_user_id
        super().__init__(f"Access denied. You do not have permission to access data of user with id {self.target_user_id}.")
