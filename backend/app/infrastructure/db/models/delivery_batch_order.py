# app/infrastructure/db/models/delivery_batch_order.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DeliveryBatchOrder(Base):
    __tablename__ = "delivery_batch_orders"
    __table_args__ = (
        Index("idx_delivery_batch_orders_order_id", "order_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    batch_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("delivery_batches.id", name="fk_delivery_batch_orders_batch_id"),
        primary_key=True,
    )
    order_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("orders.id", name="fk_delivery_batch_orders_order_id"),
        primary_key=True,
    )

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    batch: Mapped["DeliveryBatch"] = relationship(
        "DeliveryBatch",
        back_populates="order_links",
        lazy="select",
    )
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="delivery_batch_links",
        lazy="select",
    )
