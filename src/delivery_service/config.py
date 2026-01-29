from __future__ import annotations

import logging
import os
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

    DATABASE_URL: str
    SQLALCHEMY_ECHO: bool = False

    REDIS_URL: str
    CURRENCY_CACHE_TTL: int = 3600

    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    CURRENCY_API_URL: str = "https://www.cbr-xml-daily.ru/daily_json.js"

    SCHEDULER_INTERVAL_MINUTES: int = 5
    SCHEDULER_RUN_ONCE: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
logger.info("✓ Settings loaded: ENV=%s pid=%s", settings.ENVIRONMENT, os.getpid())
