from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.engine import get_db
from ...database.models import PackageType
from ..schemas import PackageTypeOut

router = APIRouter(prefix="/package-types", tags=["Package Types"])


@router.get("", response_model=list[PackageTypeOut])  # type: ignore[misc]
async def list_package_types(db: AsyncSession = Depends(get_db)) -> list[PackageTypeOut]:
    result = await db.execute(select(PackageType).order_by(PackageType.id))
    return [PackageTypeOut(id=pt.id, name=pt.name) for pt in result.scalars().all()]
