from __future__ import annotations


def test_error_schemas_import() -> None:
    # Просто импорт, чтобы файл исполнился и попал в coverage.
    from delivery_service.api import error_schemas  # noqa: F401
