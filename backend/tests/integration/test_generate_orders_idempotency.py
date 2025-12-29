from datetime import date
from app.jobs.tasks.generate_orders import run_generate_orders


def test_generate_orders_is_idempotent(uow_factory):
    delivery_date = date(2025, 1, 1)

    first = run_generate_orders(uow_factory, delivery_date)
    assert (first["created"] + first["existing"]) > 0, (
        "No due subscriptions found for this delivery_date. "
        "Seed test data (subscriptions) before running integration tests."
    )

    second = run_generate_orders(uow_factory, delivery_date)

    assert second["created"] == 0
    assert second["existing"] >= first["created"]
