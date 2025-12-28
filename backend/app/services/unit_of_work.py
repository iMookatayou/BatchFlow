# app/services/unit_of_work.py
from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.interfaces.subscription_repo import SubscriptionRepo
from app.repositories.interfaces.order_repo import OrderRepo
from app.repositories.interfaces.delivery_batch_repo import DeliveryBatchRepo

from app.infrastructure.repos_sqlalchemy.subscription_repo import SqlAlchemySubscriptionRepo
from app.infrastructure.repos_sqlalchemy.order_repo import SqlAlchemyOrderRepo
from app.infrastructure.repos_sqlalchemy.delivery_batch_repo import SqlAlchemyDeliveryBatchRepo


@dataclass
class UnitOfWork(AbstractContextManager):
    session: Session

    subscriptions: SubscriptionRepo = None  # type: ignore[assignment]
    orders: OrderRepo = None                # type: ignore[assignment]
    batches: DeliveryBatchRepo = None       # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.subscriptions = SqlAlchemySubscriptionRepo(self.session)
        self.orders = SqlAlchemyOrderRepo(self.session)
        self.batches = SqlAlchemyDeliveryBatchRepo(self.session)

    def __enter__(self) -> "UnitOfWork":
        # Session ถูกสร้างจาก DI (dependencies.py) อยู่แล้ว
        return self

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def __exit__(self, exc_type, exc, tb) -> Optional[bool]:
        if exc:
            self.rollback()
            return False
        self.commit()
        return None
