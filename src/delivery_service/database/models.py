from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


def generate_uuid_str() -> str:
    return str(uuid4())


class PackageType(Base):
    __tablename__ = "package_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Связь "тип -> посылки" оставляем
    packages: Mapped[list[Package]] = relationship("Package", back_populates="package_type")


class Package(Base):
    __tablename__ = "packages"

    # По ТЗ: id посылки должен быть доступен только в рамках сессии.
    # Делать UUID строкой проще всего: сложно перебрать + удобно в API.
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)

    # Главная привязка к "пользователю" (без авторизации): session_id из cookie.
    session_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)

    package_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("package_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)  # вес в кг
    content_value_usd: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_cost_rub: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    package_type: Mapped[PackageType] = relationship("PackageType", back_populates="packages")
