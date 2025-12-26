# app/infrastructure/db/models/delivery_batch.py
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DeliveryBatch(Base):
    __tablename__ = "delivery_batches"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_delivery_batches_public_id"),
        UniqueConstraint("batch_code", name="uq_delivery_batches_batch_code"),
        Index("idx_delivery_batches_delivery_date_zone_id", "delivery_date", "zone_id"),
        Index("idx_delivery_batches_status_cutoff_at", "status", "cutoff_at"),
        Index("idx_delivery_batches_zone_id", "zone_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(26), nullable=True)

    batch_code: Mapped[str] = mapped_column(String(32), nullable=False)
    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)

    zone_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("zones.id", name="fk_delivery_batches_zone_id"),
        nullable=True,
    )

    cutoff_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    status: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False)

    locked_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    zone: Mapped[Optional["Zone"]] = relationship(
        "Zone",
        back_populates="delivery_batches",
        lazy="select",
    )
    order_links: Mapped[List["DeliveryBatchOrder"]] = relationship(
        "DeliveryBatchOrder",
        back_populates="batch",
        lazy="select",
    )
