from __future__ import annotations

import asyncio
import logging
from decimal import Decimal

import httpx
import redis

from ..config import settings
from ..utils.cache import cache_get, cache_set

USD_RUB_CACHE_KEY = "currency:usd_rub"
logger = logging.getLogger(__name__)

# HTTPX позволяет тонко настраивать connect/read/write/pool таймауты. [web:929]
CBR_TIMEOUT = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=5.0)


async def get_usd_rub_rate() -> Decimal:
    cached: str | None = None

    # Cache read (best-effort). Ошибки Redis нужно обрабатывать. [web:916]
    try:
        cached = await cache_get(USD_RUB_CACHE_KEY)
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        logger.warning("Redis cache_get failed, fallback to CBR", exc_info=True)

    if cached:
        try:
            return Decimal(cached)
        except Exception:
            logger.warning("Bad cached USD/RUB value=%r, fallback to CBR", cached, exc_info=True)

    last_exc: Exception | None = None

    # Fetch from CBR with small retry/backoff (to survive short outages).
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=CBR_TIMEOUT) as client:
                resp = await client.get(settings.CURRENCY_API_URL)
                resp.raise_for_status()
                data = resp.json()

            # В daily_json.js курс USD лежит в Valute -> USD -> Value. [web:901]
            rate = Decimal(str(data["Valute"]["USD"]["Value"]))

            # Cache write (best-effort). Ошибки Redis нужно обрабатывать. [web:916]
            try:
                await cache_set(USD_RUB_CACHE_KEY, str(rate), settings.CURRENCY_CACHE_TTL)
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                logger.warning("Redis cache_set failed (rate=%s)", rate, exc_info=True)

            return rate

        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as e:
            last_exc = e
            if attempt < 2:
                await asyncio.sleep(0.3 * (attempt + 1))
                continue
            raise

    assert last_exc is not None
    raise last_exc
