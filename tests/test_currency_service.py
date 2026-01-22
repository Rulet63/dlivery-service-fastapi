from __future__ import annotations

from decimal import Decimal

import httpx
import pytest
import redis

from delivery_service.services import currency


@pytest.mark.anyio
async def test_currency_rate_from_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_cache_get(key: str) -> str | None:
        assert key == currency.USD_RUB_CACHE_KEY
        return "90.12"

    monkeypatch.setattr(currency, "cache_get", fake_cache_get)

    rate = await currency.get_usd_rub_rate()
    assert rate == Decimal("90.12")


@pytest.mark.anyio
async def test_currency_redis_down_fallback_to_http(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_cache_get(key: str) -> str | None:
        raise redis.exceptions.ConnectionError("redis down")

    async def fake_cache_set(key: str, value: str, ttl: int) -> None:
        return None

    class FakeResp:
        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"Valute": {"USD": {"Value": 91.0}}}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url: str):
            return FakeResp()

    monkeypatch.setattr(currency, "cache_get", fake_cache_get)
    monkeypatch.setattr(currency, "cache_set", fake_cache_set)
    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **kw: FakeClient())

    rate = await currency.get_usd_rub_rate()
    assert rate == Decimal("91.0")


@pytest.mark.anyio
async def test_currency_http_retries_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_cache_get(key: str) -> str | None:
        return None

    monkeypatch.setattr(currency, "cache_get", fake_cache_get)

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(currency.asyncio, "sleep", fake_sleep)

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url: str):
            raise httpx.RequestError("network down", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **kw: FakeClient())

    with pytest.raises(httpx.RequestError):
        await currency.get_usd_rub_rate()
