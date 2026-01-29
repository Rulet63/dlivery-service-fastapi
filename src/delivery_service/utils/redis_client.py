from __future__ import annotations

import logging
from typing import Any, Final, cast

import redis.asyncio as redis

from ..config import settings

logger = logging.getLogger(__name__)

MAX_CONNECTIONS: Final[int] = 20

_pool: redis.ConnectionPool[Any] | None = None
_redis: Any | None = None


def get_redis() -> Any:
    global _pool, _redis

    if _redis is None:
        _pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=MAX_CONNECTIONS,
        )
        _redis = cast(Any, redis.Redis(connection_pool=_pool))

    return _redis


async def close_redis() -> None:
    global _pool, _redis
    logger.info("Closing Redis client and pool")

    if _redis is not None:
        await _redis.aclose()
        _redis = None

    if _pool is not None:
        await _pool.aclose()  # type: ignore[attr-defined]
        _pool = None
