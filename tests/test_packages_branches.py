from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_packages_create_then_get_by_id_unpriced_has_not_calculated(
    app_client: AsyncClient,
) -> None:
    payload = {"name": "Book", "weight": 1.0, "package_type_id": 1, "content_value_usd": 10}
    r = await app_client.post("/api/packages", json=payload)
    assert r.status_code == 201
    package_id = r.json()["id"]

    r = await app_client.get(f"/api/packages/{package_id}")
    assert r.status_code == 200
    data = r.json()

    assert data["id"] == package_id
    assert data["delivery_cost_rub"] is None
    assert data["delivery_cost"] == "Не рассчитано"


@pytest.mark.anyio
async def test_packages_get_list_priced_true_after_recalc_has_formatted_cost(
    app_client: AsyncClient,
) -> None:
    payload = {"name": "Phone", "weight": 0.4, "package_type_id": 2, "content_value_usd": 600}
    r = await app_client.post("/api/packages", json=payload)
    assert r.status_code == 201

    r = await app_client.post("/api/debug/recalculate-delivery")
    assert r.status_code == 200

    r = await app_client.get("/api/packages", params={"limit": 50, "offset": 0, "priced": "true"})
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 1

    assert all(item["delivery_cost_rub"] is not None for item in items)
    assert all(
        isinstance(item["delivery_cost"], str) and item["delivery_cost"] != "Не рассчитано"
        for item in items
    )


@pytest.mark.anyio
async def test_packages_filter_by_type_id(
    app_client: AsyncClient,
) -> None:
    p1 = {"name": "Tshirt", "weight": 0.2, "package_type_id": 1, "content_value_usd": 20}
    p2 = {"name": "Phone", "weight": 0.4, "package_type_id": 2, "content_value_usd": 600}
    assert (await app_client.post("/api/packages", json=p1)).status_code == 201
    assert (await app_client.post("/api/packages", json=p2)).status_code == 201

    r = await app_client.get(
        "/api/packages", params={"limit": 50, "offset": 0, "package_type_id": 1}
    )
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 1
    assert all(item["package_type_id"] == 1 for item in items)


@pytest.mark.anyio
async def test_packages_invalid_package_type_id_query_422(
    app_client: AsyncClient,
) -> None:
    r = await app_client.get(
        "/api/packages", params={"limit": 10, "offset": 0, "package_type_id": 0}
    )
    assert r.status_code == 422
