from __future__ import annotations

from decimal import Decimal

import pytest
from delivery_service.database.models import Package
from delivery_service.services import recalculate
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_recalculate_returns_0_when_no_packages(
    db_session: AsyncSession, monkeypatch
) -> None:
    async def fake_rate() -> Decimal:
        return Decimal("90.00")

    monkeypatch.setattr(recalculate, "get_usd_rub_rate", fake_rate)

    updated = await recalculate.recalculate_unpriced_packages(db_session)
    assert updated == 0


@pytest.mark.anyio
async def test_recalculate_updates_delivery_cost(db_session: AsyncSession, monkeypatch) -> None:
    async def fake_rate() -> Decimal:
        return Decimal("100.00")

    monkeypatch.setattr(recalculate, "get_usd_rub_rate", fake_rate)

    p = Package(
        name="Test",
        weight=1.0,
        package_type_id=1,
        content_value_usd=10,
        session_id="test-session",
    )
    db_session.add(p)
    await db_session.commit()

    updated = await recalculate.recalculate_unpriced_packages(db_session)
    assert updated == 1

    await db_session.refresh(p)
    assert p.delivery_cost_rub is not None
