from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_packages_list_and_get_by_id_cover_item_mapping(app_client: AsyncClient) -> None:
    payload = {"name": "CoverMe", "weight": 0.5, "package_type_id": 1, "content_value_usd": 10}
    r = await app_client.post("/api/packages", json=payload)
    assert r.status_code == 201
    package_id = r.json()["id"]

    r = await app_client.get("/api/packages", params={"limit": 10, "offset": 0})
    assert r.status_code == 200
    items = r.json()["items"]
    assert any(item["id"] == package_id for item in items)

    r = await app_client.get(f"/api/packages/{package_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == package_id
    assert "delivery_cost" in data
