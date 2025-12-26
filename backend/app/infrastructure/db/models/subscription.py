# app/infrastructure/db/models/subscription.py
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_subscriptions_public_id"),
        Index("idx_subscriptions_user_id_status", "user_id", "status"),
        Index("idx_subscriptions_status_next_run_date", "status", "next_run_date"),
        Index("idx_subscriptions_plan_id", "plan_id"),
        Index("idx_subscriptions_default_address_id", "default_address_id"),
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
        ForeignKey("users.id", name="fk_subscriptions_user_id"),
        nullable=False,
    )
    plan_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("plans.id", name="fk_subscriptions_plan_id"),
        nullable=False,
    )

    status: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_run_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default="Asia/Bangkok")

    default_address_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("addresses.id", name="fk_subscriptions_default_address_id"),
        nullable=True,
    )

    paused_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions", lazy="select")
    plan: Mapped["Plan"] = relationship("Plan", back_populates="subscriptions", lazy="select")
    default_address: Mapped[Optional["Address"]] = relationship(
        "Address",
        back_populates="subscriptions_default_here",
        lazy="select",
        foreign_keys=[default_address_id],
    )

    items: Mapped[List["SubscriptionItem"]] = relationship(
        "SubscriptionItem",
        back_populates="subscription",
        lazy="select",
    )

    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="subscription",
        lazy="select",
    )
