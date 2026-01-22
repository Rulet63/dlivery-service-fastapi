from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.database.models import Package
from delivery_service.services.currency import get_usd_rub_rate


def calculate_delivery_cost_rub(
    weight_kg: float, content_value_usd: float, usd_rub: Decimal
) -> Decimal:
    cost = (
        Decimal(str(weight_kg)) * Decimal("0.5") + Decimal(str(content_value_usd)) * Decimal("0.01")
    ) * usd_rub
    return cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def recalculate_unpriced_packages(db: AsyncSession) -> int:
    usd_rub = await get_usd_rub_rate()

    result = await db.execute(select(Package).where(Package.delivery_cost_rub.is_(None)))
    packages = list(result.scalars().all())
    if not packages:
        return 0

    for p in packages:
        p.delivery_cost_rub = calculate_delivery_cost_rub(p.weight, p.content_value_usd, usd_rub)

    await db.commit()
    return len(packages)
