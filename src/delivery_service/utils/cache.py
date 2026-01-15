from __future__ import annotations

from functools import lru_cache

import redis.asyncio as redis
from redis.asyncio.client import Redis

from ..config import settings


@lru_cache(maxsize=1)
def get_redis() -> Redis[str]:
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


async def cache_get(key: str) -> str | None:
    r = get_redis()
    return await r.get(key)


async def cache_set(key: str, value: str, ttl_seconds: int) -> None:
    r = get_redis()
    await r.setex(key, ttl_seconds, value)
