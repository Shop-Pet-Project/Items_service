class AuthApplicationsError(Exception):
    """Базовый класс исключений для AuthApplicationsService."""

    pass


class InvalidCredentialsError(AuthApplicationsError):
    """Базовый класс исключений для неверных учетных данных."""

    pass


class InvalidUsernameError(InvalidCredentialsError):
    """Исключение для неверного username."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Invalid username: {username}")


class InvalidPasswordError(InvalidCredentialsError):
    """Исключение для неверного пароля."""

    def __init__(self):
        super().__init__("Invalid password")
