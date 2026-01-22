from __future__ import annotations

import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database.engine import SessionLocal
from ..services.recalculate import recalculate_unpriced_packages

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


async def process_unpriced_packages(db: AsyncSession) -> int:
    return await recalculate_unpriced_packages(db)


async def job_wrapper() -> None:
    try:
        async with SessionLocal() as session:
            updated = await process_unpriced_packages(session)
        logger.info("Delivery cost job done. Updated=%s", updated)
    except Exception:
        logger.exception("Delivery cost job failed")


async def main() -> None:
    if settings.SCHEDULER_RUN_ONCE:
        await job_wrapper()
        return

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        job_wrapper,
        trigger=CronTrigger(minute="*/5"),
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
