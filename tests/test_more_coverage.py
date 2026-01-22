from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_b1_packages_empty_list(app_client: AsyncClient) -> None:
    r = await app_client.get("/api/packages", params={"limit": 10, "offset": 0})
    assert r.status_code == 200
    data = r.json()
    assert data == {"items": [], "total": 0, "limit": 10, "offset": 0}


@pytest.mark.anyio
async def test_b2_packages_filter_priced_false(app_client: AsyncClient) -> None:
    # Создаём посылку, но НЕ запускаем пересчёт доставки
    payload = {"name": "Book", "weight": 1.0, "package_type_id": 1, "content_value_usd": 10}
    r = await app_client.post("/api/packages", json=payload)
    assert r.status_code == 201
    package_id = r.json()["id"]

    r = await app_client.get("/api/packages", params={"limit": 50, "offset": 0, "priced": "false"})
    assert r.status_code == 200
    items = r.json()["items"]

    assert any(item["id"] == package_id for item in items)
    assert all(item["delivery_cost_rub"] is None for item in items)


@pytest.mark.anyio
async def test_b3_packages_pagination_limit_offset(app_client: AsyncClient) -> None:
    # Делаем 3 посылки
    for i in range(3):
        payload = {"name": f"Item{i}", "weight": 0.1, "package_type_id": 1, "content_value_usd": 1}
        r = await app_client.post("/api/packages", json=payload)
        assert r.status_code == 201

    r1 = await app_client.get("/api/packages", params={"limit": 2, "offset": 0})
    r2 = await app_client.get("/api/packages", params={"limit": 2, "offset": 2})

    assert r1.status_code == 200
    assert r2.status_code == 200

    d1 = r1.json()
    d2 = r2.json()

    assert d1["limit"] == 2
    assert d1["offset"] == 0
    assert len(d1["items"]) == 2

    assert d2["limit"] == 2
    assert d2["offset"] == 2
    assert len(d2["items"]) >= 1


@pytest.mark.anyio
async def test_b4_packages_invalid_limit_422(app_client: AsyncClient) -> None:
    # Если у тебя Query(ge=1) или аналогичная валидация — должен быть 422
    r = await app_client.get("/api/packages", params={"limit": 0, "offset": 0})
    assert r.status_code == 422
