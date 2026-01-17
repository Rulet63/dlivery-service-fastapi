from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ApiError(BaseModel):
    error_code: str
    message: str
    details: Any | None = None
