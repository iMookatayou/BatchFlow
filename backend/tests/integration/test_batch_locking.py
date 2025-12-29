# tests/integration/test_batch_locking.py
from datetime import date, datetime

from app.jobs.tasks.generate_orders import run_generate_orders
from app.jobs.tasks.create_batches import run_create_batches
from app.jobs.tasks.lock_batches import run_lock_batches


def test_locked_batches_are_not_modified(uow_factory):
    delivery_date = date(2025, 1, 1)

    gen = run_generate_orders(uow_factory, delivery_date)
    assert (gen["created"] + gen["existing"]) > 0, (
        "No due subscriptions found for this delivery_date. "
        "Seed test data (subscriptions) before running integration tests."
    )

    first = run_create_batches(uow_factory, delivery_date)
    assert first["orders_attached"] > 0, (
        "No orders were attached on first create_batches run. "
        "Check eligible order status or seed data."
    )

    # lock batch (deterministic time)
    run_lock_batches(uow_factory, delivery_date, now=datetime(2025, 1, 1, 0, 0, 0))

    # รัน create_batches อีกครั้ง → ต้องไม่เปลี่ยนอะไร
    result = run_create_batches(uow_factory, delivery_date)

    assert result["orders_attached"] == 0
    assert result["batches_created"] == 0
