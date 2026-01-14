from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    packages: Mapped[list[Package]] = relationship(
        "Package",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class PackageType(Base):
    __tablename__ = "package_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    packages: Mapped[list[Package]] = relationship("Package", back_populates="package_type")


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    package_type_id = Column(Integer, ForeignKey("package_types.id", ondelete="RESTRICT"), nullable=False)

    name = Column(String(200), nullable=False)
    weight = Column(Float, nullable=False)
    content_value_usd = Column(Float, nullable=False)
    delivery_cost_rub = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="packages")
    package_type: Mapped[PackageType] = relationship("PackageType", back_populates="packages")
