from __future__ import annotations

from typing import cast

from .redis_client import get_redis


async def cache_get(key: str) -> str | None:
    value = await get_redis().get(key)
    return cast("str | None", value)


async def cache_set(key: str, value: str, ttl_seconds: int) -> None:
    await get_redis().setex(key, ttl_seconds, value)
