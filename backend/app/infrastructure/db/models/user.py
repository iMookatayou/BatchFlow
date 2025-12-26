# app/infrastructure/db/models/user.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_users_public_id"),
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("phone", name="uq_users_phone"),
        Index("idx_users_is_active", "is_active"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(26), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[int] = mapped_column(
        TINYINT(1),
        nullable=False,
        server_default="1",
    )
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(mysql.DATETIME(fsp=3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    addresses: Mapped[List["Address"]] = relationship(
        "Address",
        back_populates="user",
        lazy="select",
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        lazy="select",
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user",
        lazy="select",
    )
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        lazy="select",
    )

    uploaded_payment_slips: Mapped[List["PaymentSlip"]] = relationship(
        "PaymentSlip",
        back_populates="uploaded_by_user",
        lazy="select",
        foreign_keys="PaymentSlip.uploaded_by_user_id",
    )
    verified_payment_slips: Mapped[List["PaymentSlip"]] = relationship(
        "PaymentSlip",
        back_populates="verified_by_user",
        lazy="select",
        foreign_keys="PaymentSlip.verified_by_user_id",
    )
