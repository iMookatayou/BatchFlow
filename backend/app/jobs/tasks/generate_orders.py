# app/jobs/tasks/generate_orders.py
from __future__ import annotations

from datetime import date
from typing import Callable

from app.services.unit_of_work import UnitOfWork
from app.services.order_service import OrderService


def run_generate_orders(
    uow_factory: Callable[[], UnitOfWork],
    delivery_date: date,
    page_size: int = 200,
) -> dict:
    created = 0
    existing = 0
    offset = 0

    while True:
        # read page of eligible subscriptions (read txn)
        uow = uow_factory()
        with uow:
            subs = uow.subscriptions.list_due_active(delivery_date, limit=page_size, offset=offset)

        if not subs:
            break

        for sub in subs:
            # One subscription = one transaction
            uow2 = uow_factory()
            svc = OrderService(uow2)

            _, was_created = svc.generate_from_subscription(sub.id, delivery_date)
            if was_created:
                created += 1
            else:
                existing += 1

        offset += page_size

    return {"delivery_date": delivery_date.isoformat(), "created": created, "existing": existing}


def main() -> None:
    """
    CLI entrypoint for dev/ops/CI.

    Usage:
      python -m app.jobs.tasks.generate_orders 2025-12-29
      python -m app.jobs.tasks.generate_orders   # defaults to today's date
    """
    import sys

    from app.dependencies import get_db_session

    if len(sys.argv) >= 2:
        delivery_date = date.fromisoformat(sys.argv[1])
    else:
        delivery_date = date.today()

    def uow_factory() -> UnitOfWork:
        # get_db_session() is a generator dependency; grab one session per UoW
        db = next(get_db_session())
        return UnitOfWork(session=db)

    result = run_generate_orders(uow_factory=uow_factory, delivery_date=delivery_date)
    print(f"[generate_orders] {result}")


if __name__ == "__main__":
    main()
