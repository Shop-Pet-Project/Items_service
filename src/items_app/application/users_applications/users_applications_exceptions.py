from uuid import UUID


"""
Группа исключений, ограничивающая создание пользователя.
"""


class UserAlreadyExistError(Exception):
    """
    Базовый класс исключений, связанных с попыткой добавления пользователя,
    данные которых уже есть в БД.
    """

    pass


class UsernameAlreadyExistError(UserAlreadyExistError):
    """
    Исключение, выбрасываемое при попытке создании нового пользователя,
    в случае если его username уже есть в БД.

    Args:
        username (str): Username пользователя.
    """

    def __init__(self, username: str):
        self.username = username
        msg = f"User with username {self.username} already exist"
        super().__init__(msg)


class EmailAlreadyExistError(UserAlreadyExistError):
    """
    Исключение, выбрасываемое при попытке создании нового пользователя,
    в случае если его email уже есть в БД.

    Args:
        email (str): Email пользователя.
    """

    def __init__(self, email: str):
        self.email = email
        msg = f"User with email {self.email} already exist"
        super().__init__(msg)


"""
Группа исключений, обрабатывающая некорректные входные данные 
при попытке получить информацию о пользователе.
"""


class UserNotFoundError(Exception):
    """
    Базовый класс исключений, выбрасываемыех при попытке получить данные несуществуюшего пользователя.
    """

    pass


class UserIdNotFoundError(UserNotFoundError):
    """
    Исключение, выбрасываемое при попытки получить данные пользователя,
    id которого отсутствует в БД.

    Args:
        user_id (UUID): Уникальный идентификатор пользователя.
    """

    def __init__(self, user_id: UUID):
        self.user_id = user_id
        msg = f"User with ID {self.user_id} does not exist"
        super().__init__(msg)


"""
Группа исключений, ограничивающая права на доступ к пользователю.
"""


class NoAccessToUserError(Exception):
    """
    Базовый класс исключений, выбрасываемых при отказе в доступе к пользователю
    """

    pass


class NoAccessRightsError(NoAccessToUserError):
    """
    Исключение, выбрасываемое, если у пользователя нет прав доступа к операции.
    """

    def __init__(self):
        msg = "Access denied"
        super().__init__(msg)


class AccessAnotherUserDataError(NoAccessToUserError):
    """
    Исключение, возникающее при попытке получения данных пользователя
    сторонним пользователем.

    Args:
        user_id (UUID): Уникальный идентификатор пользователя.
    """

    def __init__(self, user_id: UUID):
        self.user_id = user_id
        msg = f"You do not have access to user with user_id {self.user_id}"
        super().__init__(msg)
