from __future__ import annotations

from app.infrastructure.db.models.order import Order


class OrderRepo:
    def get_by_generated_key(self, generated_key: str) -> Order | None: ...

    def add(self, order: Order) -> None: ...
