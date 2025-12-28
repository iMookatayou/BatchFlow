# app/infrastructure/db/models/subscription_item.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, UniqueConstraint, String  # ✅ add String
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SubscriptionItem(Base):
    __tablename__ = "subscription_items"
    __table_args__ = (
        UniqueConstraint(
            "subscription_id",
            "variant_id",
            name="uq_subscription_items_subscription_id_variant_id",
        ),
        Index("idx_subscription_items_subscription_id_is_active", "subscription_id", "is_active"),
        Index("idx_subscription_items_variant_id", "variant_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

    subscription_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("subscriptions.id", name="fk_subscription_items_subscription_id"),
        nullable=False,
    )
    variant_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("product_variants.id", name="fk_subscription_items_variant_id"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(INTEGER, nullable=False)

    unit_amount: Mapped[int] = mapped_column(BIGINT, nullable=False, server_default="0")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="THB")

    is_active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default="1")

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="items",
        lazy="select",
    )
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="subscription_items",
        lazy="select",
    )
