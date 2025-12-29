# tests/integration/test_create_batches.py
from datetime import date

from app.jobs.tasks.generate_orders import run_generate_orders
from app.jobs.tasks.create_batches import run_create_batches


def test_create_batches_is_idempotent(uow_factory):
    delivery_date = date(2025, 1, 1)

    gen = run_generate_orders(uow_factory, delivery_date)
    assert (gen["created"] + gen["existing"]) > 0, (
        "No due subscriptions found for this delivery_date. "
        "Seed test data (subscriptions) before running integration tests."
    )

    first = run_create_batches(uow_factory, delivery_date)
    assert (first["batches_created"] + first["orders_attached"]) > 0, (
        "create_batches did not create/attach anything on first run. "
        "Check eligible order status or seed data."
    )

    second = run_create_batches(uow_factory, delivery_date)

    assert second["batches_created"] == 0
    assert second["orders_attached"] == 0
