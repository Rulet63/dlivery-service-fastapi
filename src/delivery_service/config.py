import logging
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Конфигурация приложения (Pydantic Settings v2).
    Значения из .env файла.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # DATABASE
    DATABASE_URL: str
    SQLALCHEMY_ECHO: bool = True

    # REDIS
    REDIS_URL: str = "redis://localhost:6379/0"
    CURRENCY_CACHE_TTL: int = 3600

    # APP
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # EXTERNAL APIs
    CURRENCY_API_URL: str = "https://www.cbr-xml-daily.ru/daily_json.js"
    SCHEDULER_INTERVAL_MINUTES: int = 5


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
logger.info(f"✓ Settings loaded: ENV={settings.ENVIRONMENT}")
