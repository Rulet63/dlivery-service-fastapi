from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.database import get_db
from delivery_service.services.recalculate import recalculate_unpriced_packages

from ..schemas import RecalculateDeliveryResponse

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.post(
    "/recalculate-delivery",
    response_model=RecalculateDeliveryResponse,
    status_code=status.HTTP_200_OK,
)  # type: ignore[misc]
async def recalculate_delivery(
    db: AsyncSession = Depends(get_db),
) -> RecalculateDeliveryResponse:
    updated = await recalculate_unpriced_packages(db)
    return RecalculateDeliveryResponse(updated=updated)
