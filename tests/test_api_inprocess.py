from __future__ import annotations

import httpx
import pytest


@pytest.mark.anyio
async def test_01_get_package_types(app_client: httpx.AsyncClient) -> None:
    r = await app_client.get("/api/package-types")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert {x["id"] for x in data} == {1, 2, 3}


@pytest.mark.anyio
async def test_02_create_package_returns_id(app_client: httpx.AsyncClient) -> None:
    payload = {"name": "Phone", "weight": 0.4, "package_type_id": 2, "content_value_usd": 600}
    r = await app_client.post("/api/packages", json=payload)
    assert r.status_code == 201
    assert "id" in r.json()


@pytest.mark.anyio
async def test_03_package_flow_pricing_and_session_isolation(app_client: httpx.AsyncClient) -> None:
    payload = {"name": "Phone", "weight": 0.4, "package_type_id": 2, "content_value_usd": 600}
    r = await app_client.post("/api/packages", json=payload)
    assert r.status_code == 201
    package_id = r.json()["id"]

    r = await app_client.get("/api/packages", params={"limit": 10, "offset": 0})
    assert r.status_code == 200
    assert any(p["id"] == package_id for p in r.json()["items"])

    r = await app_client.post("/api/debug/recalculate-delivery")
    assert r.status_code == 200

    r = await app_client.get(f"/api/packages/{package_id}")
    assert r.status_code == 200
    p = r.json()
    assert p["delivery_cost"] != "Не рассчитано"
    assert p["delivery_cost_rub"] is not None

    from httpx import ASGITransport, AsyncClient

    from delivery_service.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as other:
        r = await other.get(f"/api/packages/{package_id}")
        assert r.status_code == 404


@pytest.mark.anyio
async def test_04_filters_priced_and_type(app_client: httpx.AsyncClient) -> None:
    p1 = {"name": "Tshirt", "weight": 0.2, "package_type_id": 1, "content_value_usd": 20}
    p2 = {"name": "Phone", "weight": 0.4, "package_type_id": 2, "content_value_usd": 600}

    assert (await app_client.post("/api/packages", json=p1)).status_code == 201
    assert (await app_client.post("/api/packages", json=p2)).status_code == 201

    await app_client.post("/api/debug/recalculate-delivery")

    r = await app_client.get("/api/packages", params={"limit": 50, "offset": 0, "priced": "true"})
    assert r.status_code == 200
    assert all(item["delivery_cost_rub"] is not None for item in r.json()["items"])

    r = await app_client.get(
        "/api/packages", params={"limit": 50, "offset": 0, "package_type_id": 1}
    )
    assert r.status_code == 200
    assert all(item["package_type_id"] == 1 for item in r.json()["items"])


@pytest.mark.anyio
async def test_05_validation_errors(app_client: httpx.AsyncClient) -> None:
    payload = {"name": "Phone", "weight": 0.4, "package_type_id": 999, "content_value_usd": 600}
    r = await app_client.post("/api/packages", json=payload)
    assert r.status_code == 422
    data = r.json()
    assert data["error_code"] == "unknown_package_type"
    assert "Unknown package_type_id" in data["message"]

    payload = {"name": "Phone", "package_type_id": 2}
    r = await app_client.post("/api/packages", json=payload)
    assert r.status_code == 422
    data = r.json()
    assert data["error_code"] == "validation_error"


@pytest.mark.anyio
async def test_06_package_not_found_404(app_client: httpx.AsyncClient) -> None:
    r = await app_client.get("/api/packages/12345678-1234-1234-1234-123456789abc")
    assert r.status_code == 404
    data = r.json()
    assert data["error_code"] == "not_found"


@pytest.mark.anyio
async def test_07_session_isolation_get_by_id(app_client: httpx.AsyncClient) -> None:
    payload = {"name": "Secret", "weight": 0.1, "package_type_id": 1, "content_value_usd": 10}
    r = await app_client.post("/api/packages", json=payload)
    package_id = r.json()["id"]

    from httpx import ASGITransport, AsyncClient

    from delivery_service.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as other:
        r = await other.get(f"/api/packages/{package_id}")
        assert r.status_code == 404
