# app/infrastructure/db/models/product_variant.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_product_variants_public_id"),
        UniqueConstraint("sku", name="uq_product_variants_sku"),
        Index("idx_product_variants_product_id_is_active", "product_id", "is_active"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(26), nullable=True)

    product_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("products.id", name="fk_product_variants_product_id"),
        nullable=False,
    )

    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default="1")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="variants",
        lazy="select",
    )
    inventory: Mapped[Optional["Inventory"]] = relationship(
        "Inventory",
        back_populates="variant",
        uselist=False,
        lazy="select",
    )

    subscription_items: Mapped[List["SubscriptionItem"]] = relationship(
        "SubscriptionItem",
        back_populates="variant",
        lazy="select",
    )
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="variant",
        lazy="select",
    )
