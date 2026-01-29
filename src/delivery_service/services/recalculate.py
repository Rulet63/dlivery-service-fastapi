from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.database.models import Package
from delivery_service.services.currency import get_usd_rub_rate


def calculate_delivery_cost_rub(
    weight_kg: float, content_value_usd: Decimal, usd_rub: Decimal
) -> Decimal:
    cost = (
        Decimal(str(weight_kg)) * Decimal("0.5") + content_value_usd * Decimal("0.01")
    ) * usd_rub
    return cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def recalculate_unpriced_packages(db: AsyncSession) -> int:
    any_id = await db.scalar(select(Package.id).where(Package.delivery_cost_rub.is_(None)).limit(1))
    if any_id is None:
        return 0

    usd_rub = await get_usd_rub_rate()

    result = await db.execute(select(Package).where(Package.delivery_cost_rub.is_(None)))
    packages = result.scalars().all()  # list[Package]

    for p in packages:
        p.delivery_cost_rub = calculate_delivery_cost_rub(p.weight, p.content_value_usd, usd_rub)

    await db.commit()
    return len(packages)
