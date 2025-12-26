# app/infrastructure/db/models/payment_slip.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PaymentSlip(Base):
    __tablename__ = "payment_slips"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_payment_slips_public_id"),
        Index("idx_payment_slips_payment_id", "payment_id"),
        Index("idx_payment_slips_verified_at", "verified_at"),
        Index("idx_payment_slips_uploaded_by_user_id", "uploaded_by_user_id"),
        Index("idx_payment_slips_verified_by_user_id", "verified_by_user_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(26), nullable=True)

    payment_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("payments.id", name="fk_payment_slips_payment_id"),
        nullable=False,
    )

    file_url: Mapped[str] = mapped_column(String(500), nullable=False)

    uploaded_by_user_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_payment_slips_uploaded_by_user_id"),
        nullable=True,
    )

    verified_by_user_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_payment_slips_verified_by_user_id"),
        nullable=True,
    )

    verified_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    payment: Mapped["Payment"] = relationship("Payment", back_populates="slips", lazy="select")
    uploaded_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="uploaded_payment_slips",
        lazy="select",
        foreign_keys=[uploaded_by_user_id],
    )
    verified_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="verified_payment_slips",
        lazy="select",
        foreign_keys=[verified_by_user_id],
    )
