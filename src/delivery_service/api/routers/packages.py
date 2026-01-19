from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.engine import get_db
from ...database.models import Package, PackageType
from ..deps import get_session_id
from ..schemas import PackageCreate, PackageCreatedResponse, PackageListResponse, PackageOut

router = APIRouter(prefix="/packages", tags=["Packages"])


@router.post("", response_model=PackageCreatedResponse, status_code=status.HTTP_201_CREATED)  # type: ignore[misc]
async def create_package(
    payload: PackageCreate,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
) -> PackageCreatedResponse:
    result = await db.execute(select(PackageType.id).where(PackageType.id == payload.package_type_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "unknown_package_type",
                "message": "Unknown package_type_id",
                "details": {"package_type_id": payload.package_type_id},
            },
        )

    package = Package()
    package.session_id = session_id
    package.package_type_id = payload.package_type_id
    package.name = payload.name
    package.weight = payload.weight
    package.content_value_usd = payload.content_value_usd

    db.add(package)
    await db.commit()
    await db.refresh(package)

    return PackageCreatedResponse(id=package.id)


@router.get("", response_model=PackageListResponse)  # type: ignore[misc]
async def get_packages(
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    package_type_id: int | None = Query(None, gt=0),
    priced: bool | None = None,
) -> PackageListResponse:
    base_query = (
        select(Package, PackageType.name)
        .join(PackageType, Package.package_type_id == PackageType.id)
        .where(Package.session_id == session_id)
    )

    if package_type_id is not None:
        base_query = base_query.where(Package.package_type_id == package_type_id)

    if priced is not None:
        base_query = base_query.where(
            Package.delivery_cost_rub.is_not(None) if priced else Package.delivery_cost_rub.is_(None)
        )

    count_query = (
        select(func.count())
        .select_from(Package)
        .join(PackageType, Package.package_type_id == PackageType.id)
        .where(Package.session_id == session_id)
    )

    if package_type_id is not None:
        count_query = count_query.where(Package.package_type_id == package_type_id)

    if priced is not None:
        count_query = count_query.where(
            Package.delivery_cost_rub.is_not(None) if priced else Package.delivery_cost_rub.is_(None)
        )

    total = (await db.execute(count_query)).scalar_one()

    result = await db.execute(base_query.order_by(Package.created_at.desc()).limit(limit).offset(offset))
    rows = result.all()

    items: list[PackageOut] = []
    for package, package_type_name in rows:
        delivery_cost = "Не рассчитано" if package.delivery_cost_rub is None else f"{package.delivery_cost_rub:.2f}"
        items.append(
            PackageOut(
                id=package.id,
                name=package.name,
                weight=package.weight,
                package_type_id=package.package_type_id,
                package_type_name=package_type_name,
                content_value_usd=package.content_value_usd,
                delivery_cost_rub=package.delivery_cost_rub,
                delivery_cost=delivery_cost,
            )
        )

    return PackageListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{package_id}", response_model=PackageOut)  # type: ignore[misc]
async def get_package_by_id(
    package_id: str,
    session_id: str = Depends(get_session_id),
    db: AsyncSession = Depends(get_db),
) -> PackageOut:
    result = await db.execute(
        select(Package, PackageType.name)
        .join(PackageType, Package.package_type_id == PackageType.id)
        .where(Package.id == package_id, Package.session_id == session_id)
    )
    row = result.one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "not_found", "message": "Package not found"},
        )

    package, package_type_name = row
    delivery_cost = "Не рассчитано" if package.delivery_cost_rub is None else f"{package.delivery_cost_rub:.2f}"

    return PackageOut(
        id=package.id,
        name=package.name,
        weight=package.weight,
        package_type_id=package.package_type_id,
        package_type_name=package_type_name,
        content_value_usd=package.content_value_usd,
        delivery_cost_rub=package.delivery_cost_rub,
        delivery_cost=delivery_cost,
    )
