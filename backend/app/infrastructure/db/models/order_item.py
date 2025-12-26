# app/infrastructure/db/models/order_item.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "variant_id", name="uq_order_items_order_id_variant_id"),
        Index("idx_order_items_order_id", "order_id"),
        Index("idx_order_items_variant_id", "variant_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("orders.id", name="fk_order_items_order_id"),
        nullable=False,
    )

    variant_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("product_variants.id", name="fk_order_items_variant_id"),
        nullable=False,
    )

    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    quantity: Mapped[int] = mapped_column(INTEGER, nullable=False)

    unit_amount: Mapped[int] = mapped_column(BIGINT, nullable=False, server_default="0")
    line_total_amount: Mapped[int] = mapped_column(BIGINT, nullable=False, server_default="0")

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
        lazy="select",
    )
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="order_items",
        lazy="select",
    )
