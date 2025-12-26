# app/infrastructure/db/models/address.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_addresses_public_id"),
        Index("idx_addresses_user_id_is_default", "user_id", "is_default"),
        Index("idx_addresses_zone_id", "zone_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(26), nullable=True)

    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_addresses_user_id"),
        nullable=False,
    )

    label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)

    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subdistrict: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, server_default="TH")

    zone_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("zones.id", name="fk_addresses_zone_id"),
        nullable=True,
    )

    is_default: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default="0")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="addresses", lazy="select")
    zone: Mapped[Optional["Zone"]] = relationship("Zone", back_populates="addresses", lazy="select")

    orders_shipping_here: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="shipping_address",
        lazy="select",
        foreign_keys="Order.shipping_address_id",
    )

    subscriptions_default_here: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="default_address",
        lazy="select",
        foreign_keys="Subscription.default_address_id",
    )
