# app/infrastructure/repos_sqlalchemy/order_repo.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models.order import Order


class SqlAlchemyOrderRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_generated_key(self, generated_key: str) -> Order | None:
        stmt = select(Order).where(Order.generated_key == generated_key)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, order: Order) -> None:
        self.session.add(order)
