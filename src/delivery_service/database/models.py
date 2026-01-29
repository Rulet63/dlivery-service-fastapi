from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DECIMAL, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


def generate_uuid_str() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PackageType(Base):
    __tablename__ = "package_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    packages: Mapped[list["Package"]] = relationship("Package", back_populates="package_type")


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    session_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)

    package_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("package_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)

    content_value_usd: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    delivery_cost_rub: Mapped[Decimal | None] = mapped_column(DECIMAL(12, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    package_type: Mapped["PackageType"] = relationship("PackageType", back_populates="packages")
