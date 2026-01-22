from __future__ import annotations

import pytest
from delivery_service.tasks import scheduler
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.anyio
async def test_scheduler_process_unpriced_delegates(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_recalc(db: AsyncSession) -> int:
        return 123

    # Важно: патчим именно имя в модуле scheduler
    monkeypatch.setattr(scheduler, "recalculate_unpriced_packages", fake_recalc)

    assert await scheduler.process_unpriced_packages(db_session) == 123
