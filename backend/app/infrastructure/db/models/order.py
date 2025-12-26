# app/infrastructure/db/models/order.py
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_orders_public_id"),
        UniqueConstraint("order_no", name="uq_orders_order_no"),
        UniqueConstraint("generated_key", name="uq_orders_generated_key"),
        Index("idx_orders_user_id_created_at", "user_id", "created_at"),
        Index("idx_orders_subscription_id_delivery_date", "subscription_id", "delivery_date"),
        Index("idx_orders_status_delivery_date", "status", "delivery_date"),
        Index("idx_orders_delivery_date_zone_id", "delivery_date", "zone_id"),
        Index("idx_orders_shipping_address_id", "shipping_address_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(26), nullable=True)

    order_no: Mapped[str] = mapped_column(String(32), nullable=False)

    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_orders_user_id"),
        nullable=False,
    )

    subscription_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("subscriptions.id", name="fk_orders_subscription_id"),
        nullable=True,
    )

    status: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False)

    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)

    zone_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("zones.id", name="fk_orders_zone_id"),
        nullable=True,
    )

    shipping_address_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("addresses.id", name="fk_orders_shipping_address_id"),
        nullable=False,
    )

    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="THB")

    subtotal_amount: Mapped[int] = mapped_column(BIGINT, nullable=False, server_default="0")
    shipping_amount: Mapped[int] = mapped_column(BIGINT, nullable=False, server_default="0")
    total_amount: Mapped[int] = mapped_column(BIGINT, nullable=False, server_default="0")

    generated_key: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="orders", lazy="select")
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription",
        back_populates="orders",
        lazy="select",
    )
    zone: Mapped[Optional["Zone"]] = relationship(
        "Zone",
        back_populates="orders",
        lazy="select",
    )
    shipping_address: Mapped["Address"] = relationship(
        "Address",
        back_populates="orders_shipping_here",
        lazy="select",
        foreign_keys=[shipping_address_id],
    )

    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        lazy="select",
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="order",
        lazy="select",
    )

    delivery_batch_links: Mapped[List["DeliveryBatchOrder"]] = relationship(
        "DeliveryBatchOrder",
        back_populates="order",
        lazy="select",
    )
