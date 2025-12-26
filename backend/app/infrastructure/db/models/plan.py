# app/infrastructure/db/models/plan.py
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, ENUM, SMALLINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = (
        UniqueConstraint("code", name="uq_plans_code"),
        Index("idx_plans_is_active", "is_active"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    interval_unit: Mapped[str] = mapped_column(
        ENUM("day", "week", "month", name="plans_interval_unit"),
        nullable=False,
    )
    interval_count: Mapped[int] = mapped_column(SMALLINT(unsigned=True), nullable=False)

    is_active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default="1")

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="plan",
        lazy="select",
    )
