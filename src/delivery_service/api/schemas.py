from __future__ import annotations

from pydantic import BaseModel, Field


class PackageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    weight: float = Field(gt=0)  # кг
    package_type_id: int = Field(gt=0)
    content_value_usd: float = Field(ge=0)


class PackageCreatedResponse(BaseModel):
    id: str


class PackageTypeOut(BaseModel):
    id: int
    name: str


class PackageOut(BaseModel):
    id: str
    name: str
    weight: float
    package_type_id: int
    package_type_name: str
    content_value_usd: float
    delivery_cost_rub: float | None
    delivery_cost: str


class PackageListResponse(BaseModel):
    items: list[PackageOut]
    total: int
    limit: int
    offset: int
