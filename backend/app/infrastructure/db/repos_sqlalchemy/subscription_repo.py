from __future__ import annotations

from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.infrastructure.db.models.subscription import Subscription


# NOTE: ค่า status “ACTIVE” ต้องตรงกับระบบคุณ
# ถ้ามี domain enum อยู่แล้ว ให้ import มาแทน
SUBSCRIPTION_STATUS_ACTIVE = 1


class SqlAlchemySubscriptionRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, subscription_id: int) -> Subscription | None:
        stmt = select(Subscription).where(Subscription.id == subscription_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def lock_by_id(self, subscription_id: int) -> Subscription | None:
        stmt = (
            select(Subscription)
            .where(Subscription.id == subscription_id)
            .with_for_update()
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_due_active(self, cycle_date: date, limit: int, offset: int = 0) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .where(
                and_(
                    Subscription.status == SUBSCRIPTION_STATUS_ACTIVE,
                    Subscription.next_run_date <= cycle_date,
                    Subscription.paused_at.is_(None),
                    Subscription.canceled_at.is_(None),
                    Subscription.deleted_at.is_(None),
                )
            )
            .order_by(Subscription.id.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(stmt).scalars().all())
