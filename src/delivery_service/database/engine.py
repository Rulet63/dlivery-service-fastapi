# заглушка
from __future__ import annotations

from collections.abc import Generator
from typing import Any

engine: Any = None
SessionLocal: Any = None


def get_db() -> Generator[Any, None, None]:
    yield None
