"""Database layer with models and connections."""

from __future__ import annotations

from .engine import SessionLocal, engine, get_db
from .models import Base, Package, PackageType

__all__ = [
    "Base",
    "Package",
    "PackageType",
    "engine",
    "SessionLocal",
    "get_db",
]


def init_db() -> None:
    """Инициализация БД.

    В этом проекте схемой управляет Alembic миграциями,
    поэтому create_all на старте не используется.
    """
    return None
