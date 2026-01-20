import os
from collections.abc import AsyncGenerator

import httpx
import pytest

BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as c:
        yield c


@pytest.mark.anyio
async def test_01_get_package_types(client: httpx.AsyncClient) -> None:
    r = await client.get("/api/package-types")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert {x["id"] for x in data} == {1, 2, 3}


@pytest.mark.anyio
async def test_02_create_package_returns_id(client: httpx.AsyncClient) -> None:
    payload = {"name": "Phone", "weight": 0.4, "package_type_id": 2, "content_value_usd": 600}
    r = await client.post("/api/packages", json=payload)
    assert r.status_code == 201
    assert "id" in r.json()


@pytest.mark.anyio
async def test_03_package_flow_pricing_and_session_isolation(client: httpx.AsyncClient) -> None:
    payload = {"name": "Phone", "weight": 0.4, "package_type_id": 2, "content_value_usd": 600}
    r = await client.post("/api/packages", json=payload)
    assert r.status_code == 201
    package_id = r.json()["id"]

    r = await client.get("/api/packages", params={"limit": 10, "offset": 0})
    assert r.status_code == 200
    assert any(p["id"] == package_id for p in r.json()["items"])

    r = await client.post("/api/debug/recalculate-delivery")
    assert r.status_code == 200

    r = await client.get(f"/api/packages/{package_id}")
    assert r.status_code == 200
    p = r.json()
    assert p["delivery_cost"] != "Не рассчитано"
    assert p["delivery_cost_rub"] is not None

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as other:
        r = await other.get(f"/api/packages/{package_id}")
        assert r.status_code == 404


@pytest.mark.anyio
async def test_04_filters_priced_and_type(client: httpx.AsyncClient) -> None:
    p1 = {"name": "Tshirt", "weight": 0.2, "package_type_id": 1, "content_value_usd": 20}
    p2 = {"name": "Phone", "weight": 0.4, "package_type_id": 2, "content_value_usd": 600}

    assert (await client.post("/api/packages", json=p1)).status_code == 201
    assert (await client.post("/api/packages", json=p2)).status_code == 201

    await client.post("/api/debug/recalculate-delivery")

    r = await client.get("/api/packages", params={"limit": 50, "offset": 0, "priced": "true"})
    assert r.status_code == 200
    assert all(item["delivery_cost_rub"] is not None for item in r.json()["items"])

    r = await client.get("/api/packages", params={"limit": 50, "offset": 0, "package_type_id": 1})
    assert r.status_code == 200
    assert all(item["package_type_id"] == 1 for item in r.json()["items"])


@pytest.mark.anyio
async def test_05_validation_errors(client: httpx.AsyncClient) -> None:
    # invalid package_type_id -> business validation error
    payload = {"name": "Phone", "weight": 0.4, "package_type_id": 999, "content_value_usd": 600}
    r = await client.post("/api/packages", json=payload)
    assert r.status_code == 422
    data = r.json()
    assert data["error_code"] == "unknown_package_type"  # ваш бизнес-ошибка
    assert "Unknown package_type_id" in data["message"]

    # missing required field -> Pydantic validation error
    payload = {"name": "Phone", "package_type_id": 2}  # no weight/content_value_usd
    r = await client.post("/api/packages", json=payload)
    assert r.status_code == 422
    data = r.json()
    assert data["error_code"] == "validation_error"  # Pydantic


@pytest.mark.anyio
async def test_06_package_not_found_404(client: httpx.AsyncClient) -> None:
    # get non-existing package id
    r = await client.get("/api/packages/12345678-1234-1234-1234-123456789abc")
    assert r.status_code == 404
    data = r.json()
    assert data["error_code"] == "not_found"


@pytest.mark.anyio
async def test_07_session_isolation_get_by_id(client: httpx.AsyncClient) -> None:
    # create package in session A
    payload = {"name": "Secret", "weight": 0.1, "package_type_id": 1, "content_value_usd": 10}
    r = await client.post("/api/packages", json=payload)
    package_id = r.json()["id"]

    # session B should not access it
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as other:
        r = await other.get(f"/api/packages/{package_id}")
        assert r.status_code == 404
