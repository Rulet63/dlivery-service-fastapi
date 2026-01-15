from __future__ import annotations

from decimal import Decimal

import httpx

from ..config import settings
from ..utils.cache import cache_get, cache_set

USD_RUB_CACHE_KEY = "currency:usd_rub"


async def get_usd_rub_rate() -> Decimal:
    cached = await cache_get(USD_RUB_CACHE_KEY)
    if cached:
        return Decimal(cached)

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(settings.CURRENCY_API_URL)
        resp.raise_for_status()
        data = resp.json()

    # В daily_json.js курс USD лежит в Valute -> USD -> Value
    rate = Decimal(str(data["Valute"]["USD"]["Value"]))

    await cache_set(USD_RUB_CACHE_KEY, str(rate), settings.CURRENCY_CACHE_TTL)
    return rate
