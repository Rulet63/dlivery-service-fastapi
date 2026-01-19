from __future__ import annotations

from fastapi import APIRouter, status

from ...tasks.scheduler import process_unpriced_packages
from ..schemas import RecalculateDeliveryResponse

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.post(
    "/recalculate-delivery",
    response_model=RecalculateDeliveryResponse,
    status_code=status.HTTP_200_OK,
)  # type: ignore[misc]
async def recalculate_delivery() -> RecalculateDeliveryResponse:
    updated = await process_unpriced_packages()
    return RecalculateDeliveryResponse(updated=updated)
