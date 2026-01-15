from __future__ import annotations

import asyncio
import logging
import signal
from decimal import Decimal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from ..config import settings
from ..database.engine import SessionLocal
from ..database.models import Package
from ..services.currency import get_usd_rub_rate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


def calculate_delivery_cost_rub(weight_kg: float, content_value_usd: float, usd_rub: Decimal) -> float:
    cost = (Decimal(str(weight_kg)) * Decimal("0.5") + Decimal(str(content_value_usd)) * Decimal("0.01")) * usd_rub
    return float(cost)


async def process_unpriced_packages() -> int:
    usd_rub = await get_usd_rub_rate()

    async with SessionLocal() as session:
        result = await session.execute(select(Package).where(Package.delivery_cost_rub.is_(None)))
        packages = list(result.scalars().all())

        for p in packages:
            p.delivery_cost_rub = calculate_delivery_cost_rub(p.weight, p.content_value_usd, usd_rub)

        await session.commit()
        return len(packages)


async def job_wrapper() -> None:
    try:
        updated = await process_unpriced_packages()
        logger.info("Delivery cost job done. Updated=%s", updated)
    except Exception:
        logger.exception("Delivery cost job failed")


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        job_wrapper,
        trigger="interval",
        minutes=settings.SCHEDULER_INTERVAL_MINUTES,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()

    stop_event = asyncio.Event()

    def _stop() -> None:
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, _stop)
    loop.add_signal_handler(signal.SIGINT, _stop)

    await stop_event.wait()
    scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
