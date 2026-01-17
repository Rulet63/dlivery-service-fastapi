from __future__ import annotations

from fastapi import APIRouter, status

from ...tasks.scheduler import process_unpriced_packages

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.post("/recalculate-delivery", status_code=status.HTTP_200_OK)  # type: ignore[misc]
async def recalculate_delivery() -> dict[str, int]:
    updated = await process_unpriced_packages()
    return {"updated": updated}
