# app/infrastructure/db/models/user_role.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        Index("idx_user_roles_role_id", "role_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_user_roles_user_id"),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("roles.id", name="fk_user_roles_role_id"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(mysql.DATETIME(fsp=3), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_roles", lazy="select")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles", lazy="select")
