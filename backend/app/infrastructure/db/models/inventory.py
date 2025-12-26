# app/infrastructure/db/models/inventory.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    variant_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("product_variants.id", name="fk_inventory_variant_id"),
        primary_key=True,
    )

    qty_on_hand: Mapped[int] = mapped_column(INTEGER, nullable=False, server_default="0")
    qty_reserved: Mapped[int] = mapped_column(INTEGER, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="inventory",
        lazy="select",
    )
