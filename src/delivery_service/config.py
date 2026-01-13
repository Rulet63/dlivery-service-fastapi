import logging
from functools import lru_cache

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Конфигурация приложения (Pydantic v2).
    Значения из .env файла.
    """

    # ============================================================
    # DATABASE
    # ============================================================
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/delivery_db"
    SQLALCHEMY_ECHO: bool = True

    # ============================================================
    # REDIS (один пакет redis для sync и async!)
    # ============================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    CURRENCY_CACHE_TTL: int = 3600  # 1 час

    # ============================================================
    # ПРИЛОЖЕНИЕ
    # ============================================================
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"  # development, staging, production

    # ============================================================
    # ВНЕШНИЕ API
    # ============================================================
    CURRENCY_API_URL: str = "https://www.cbr-xml-daily.ru/daily_json.js"
    SCHEDULER_INTERVAL_MINUTES: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


# Кешируем конфиг чтобы не парсить .env каждый раз
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Получить конфиг (кешированно)"""
    return Settings()


# Глобальный объект настроек
settings = get_settings()

logger.info(f"✓ Settings loaded: ENV={settings.ENVIRONMENT}")
