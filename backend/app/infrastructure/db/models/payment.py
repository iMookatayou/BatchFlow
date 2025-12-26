# app/infrastructure/db/models/payment.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_payments_public_id"),
        UniqueConstraint("provider", "provider_ref", name="uq_payments_provider_provider_ref"),
        UniqueConstraint("idempotency_key", name="uq_payments_idempotency_key"),
        Index("idx_payments_order_id", "order_id"),
        Index("idx_payments_status_created_at", "status", "created_at"),
        Index("idx_payments_provider_provider_ref_lookup", "provider", "provider_ref"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(26), nullable=True)

    order_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("orders.id", name="fk_payments_order_id"),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)

    status: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False)

    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="THB")
    amount: Mapped[int] = mapped_column(BIGINT, nullable=False)

    provider_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    paid_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)

    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="payments",
        lazy="select",
    )
    slips: Mapped[List["PaymentSlip"]] = relationship(
        "PaymentSlip",
        back_populates="payment",
        lazy="select",
    )
