from abc import ABC, abstractmethod
from pydantic_settings import BaseSettings, SettingsConfigDict


"""
Конфигурация приложения для локальной разработки или для запуске в Docker-контейнере.
Используется для настройки подключения к базе данных и других параметров приложения.
Имеет два режима: "development" и "docker".
Для режима "development" используется локальная база данных PostgreSQL.
Для режима "docker" используется база данных PostgreSQL, запущенная в Docker-контейнере.
По умолчанию используется режим "docker".
"""


class Envoriment(BaseSettings):
    ENV_MODE: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class BaseConfig(BaseSettings, ABC):
    """
    Абстрактный, базовый класс конфигурации.
    """

    # --- Конфигурация базы данных PostgreSQL ---
    DB_ASYNC_DRIVER: str = "postgresql+asyncpg"
    DB_SYNC_DRIVER: str = "postgresql+psycopg2"
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int = 5432
    DB_NAME: str

    @property
    @abstractmethod
    def DB_HOST(self) -> str:
        """
        Абстрактный метод для получения хоста базы данных.
        Должен быть реализован в дочерних классах.
        """
        pass

    # --- Конфигурация сервиса Redis ---
    REDIS_DRIVER: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRE_SECONDS: int = 3600

    @property
    @abstractmethod
    def REDIS_HOST(self) -> str:
        """
        Абстрактный метод для получения хоста Redis.
        Должен быть реализован в дочерних классах.
        """
        pass

    # --- Свойства для формирования URL ---
    @property
    def DB_URL(self) -> str:
        """
        Формирует URL для подключения к базе данных в приложении.
        """
        return f"{self.DB_ASYNC_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ALEMBIC_DB_URL(self) -> str:
        """
        Формирует URL для Alembic.
        """
        return f"{self.DB_SYNC_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class DevelopmentConfig(BaseConfig):
    """
    Конфигурация для локальной разработки.
    Использует локальную базу данных PostgreSQL.
    """

    @property
    def DB_HOST(self) -> str:
        """
        Возвращает хост базы данных для локальной разработки.
        """
        return "localhost"

    @property
    def REDIS_HOST(self) -> str:
        """
        Возвращает хост Redis для локальной разработки.
        """
        return "localhost"


class DockerConfig(BaseConfig):
    """
    Конфигурация для запуска в Docker-контейнере.
    Использует базу данных PostgreSQL, запущенную в Docker-контейнере.
    """

    @property
    def DB_HOST(self) -> str:
        """
        Возвращает хост базы данных для Docker-контейнера.
        """
        return "postgres"

    @property
    def REDIS_HOST(self) -> str:
        """
        Возвращает хост Redis для Docker-контейнера.
        """
        return "redis"


def settings_fabric() -> BaseConfig:
    env = Envoriment()
    env_mode = env.ENV_MODE
    if env_mode == "development":
        return DevelopmentConfig()
    elif env_mode == "docker":
        return DockerConfig()
    else:
        raise TypeError


config = settings_fabric()
