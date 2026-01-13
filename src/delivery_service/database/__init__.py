"""Database layer with models and connections."""

from .engine import SessionLocal, engine, get_db
from .models import Base, Package, PackageType, User

__all__ = [
    "Base",
    "Package",
    "PackageType",
    "SessionLocal",
    "User",
    "engine",
    "get_db",
    "init_db",
]


def init_db() -> None:
    """Инициализировать базу данных.

    Создаёт все таблицы, если их нет.
    Вызывается один раз при запуске приложения.
    """
    Base.metadata.create_all(bind=engine)
