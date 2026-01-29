from __future__ import annotations

import asyncio
import logging
import random
from decimal import Decimal

import httpx
import redis

from ..config import settings
from ..schemas.cbr import CbrDailyRates
from ..utils.cache import cache_get, cache_set

USD_RUB_CACHE_KEY = "currency:usd_rub"
logger = logging.getLogger(__name__)

CBR_TIMEOUT = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=5.0)

MAX_ATTEMPTS = 3
BASE_DELAY = 0.3
MAX_DELAY = 2.0


async def get_usd_rub_rate() -> Decimal:
    try:
        cached = await cache_get(USD_RUB_CACHE_KEY)
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        logger.warning("Redis cache_get failed, fallback to CBR", exc_info=True)
        cached = None

    if cached:
        try:
            logger.debug("USD/RUB rate from cache key=%s", USD_RUB_CACHE_KEY)
            return Decimal(cached)
        except Exception:
            logger.warning("Bad cached USD/RUB value=%r, fallback to CBR", cached, exc_info=True)

    for attempt in range(MAX_ATTEMPTS):
        try:
            async with httpx.AsyncClient(timeout=CBR_TIMEOUT) as client:
                resp = await client.get(settings.CURRENCY_API_URL)
                resp.raise_for_status()
                raw = resp.json()

            data = CbrDailyRates.model_validate(raw)
            rate = data.Valute.USD.Value
            logger.info("USD/RUB rate fetched from CBR: %s", rate)

            try:
                await cache_set(USD_RUB_CACHE_KEY, str(rate), settings.CURRENCY_CACHE_TTL)
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
                logger.warning("Redis cache_set failed (rate=%s)", rate, exc_info=True)

            return rate

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            if attempt >= MAX_ATTEMPTS - 1:
                raise

            delay = min(MAX_DELAY, BASE_DELAY * (2**attempt))
            delay += random.uniform(0, delay * 0.1)

            logger.warning(
                "CBR request failed (attempt=%s/%s), retrying in %.2fs: %r",
                attempt + 1,
                MAX_ATTEMPTS,
                delay,
                e,
            )
            await asyncio.sleep(delay)

    raise RuntimeError("Unexpected control flow: retry loop exited without return/raise")
