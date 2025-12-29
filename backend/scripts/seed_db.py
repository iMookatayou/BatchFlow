# scripts/seed_db.py
from __future__ import annotations

import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.sqltypes import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)

# -----------------------------
# Make `app` importable
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

# -----------------------------
# Import models
# -----------------------------
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.address import Address
from app.infrastructure.db.models.plan import Plan
from app.infrastructure.db.models.product import Product
from app.infrastructure.db.models.product_variant import ProductVariant
from app.infrastructure.db.models.subscription import Subscription
from app.infrastructure.db.models.subscription_item import SubscriptionItem

DELIVERY_DATE = date(2025, 1, 1)


def now() -> datetime:
    return datetime.utcnow()


# -----------------------------
# Generic helpers (schema-safe)
# -----------------------------
def default_value(table: str, col: str, col_type: Any) -> Any:
    name = col.lower()

    if name in {"created_at", "updated_at"}:
        return now()

    if name == "postal_code":
        return "10110"

    if name in {"status", "is_active"}:
        return 1

    if name == "timezone":
        return "Asia/Bangkok"

    if name == "currency":
        return "THB"

    if name == "email":
        return "test@example.com"

    if name == "code":
        return f"TEST_{table.upper()}"

    if name == "sku":
        return "TEST-SKU"

    if isinstance(col_type, Date):
        return DELIVERY_DATE

    if isinstance(col_type, DateTime):
        return now()

    if isinstance(col_type, (Integer, Numeric)):
        return 1

    if isinstance(col_type, Boolean):
        return True

    if isinstance(col_type, (String, Text)):
        return f"test_{table}_{col}"

    return None


def build_required_kwargs(model, base: dict) -> dict:
    data = dict(base)
    table = model.__table__

    for col in table.columns:
        if col.name in data:
            continue
        if col.nullable:
            continue
        if col.primary_key and col.autoincrement:
            continue
        if col.server_default is not None:
            continue

        data[col.name] = default_value(table.name, col.name, col.type)

    return data


def get_or_create(session: Session, model, lookup: dict, base: dict):
    q = session.query(model)
    for k, v in lookup.items():
        q = q.filter(getattr(model, k) == v)

    obj = q.first()
    if obj:
        return obj

    payload = build_required_kwargs(model, base)
    obj = model(**payload)
    session.add(obj)
    session.flush()
    return obj


# -----------------------------
# Main seed
# -----------------------------
def main() -> None:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is required")

    engine = create_engine(db_url, future=True)
    SessionLocal = sessionmaker(bind=engine, future=True)

    with SessionLocal() as session:
        # User
        user = get_or_create(
            session,
            User,
            lookup={"email": "test@example.com"},
            base={"email": "test@example.com"},
        )

        # Address (schema-safe)
        address = get_or_create(
            session,
            Address,
            lookup={"user_id": user.id},
            base={"user_id": user.id},
        )

        # Plan
        plan = get_or_create(
            session,
            Plan,
            lookup={"code": "TEST_PLAN"},
            base={
                "code": "TEST_PLAN",
                "interval_unit": "MONTH",
                "interval_count": 1,
            },
        )

        # Product
        product = get_or_create(
            session,
            Product,
            lookup={"name": "Test Product"},
            base={"name": "Test Product"},
        )

        # Variant
        variant = get_or_create(
            session,
            ProductVariant,
            lookup={"sku": "TEST-SKU"},
            base={"product_id": product.id, "sku": "TEST-SKU"},
        )

        # Subscription
        subscription = get_or_create(
            session,
            Subscription,
            lookup={
                "user_id": user.id,
                "next_run_date": DELIVERY_DATE,
            },
            base={
                "user_id": user.id,
                "plan_id": plan.id,
                "default_address_id": address.id,
                "status": 1,
                "start_date": DELIVERY_DATE,
                "next_run_date": DELIVERY_DATE,
            },
        )

        # Subscription Item
        get_or_create(
            session,
            SubscriptionItem,
            lookup={
                "subscription_id": subscription.id,
                "variant_id": variant.id,
            },
            base={
                "subscription_id": subscription.id,
                "variant_id": variant.id,
                "quantity": 1,
                "unit_amount": 1000,
                "is_active": 1,
            },
        )
        
        # Repair existing due subscriptions
        due_subs = (
            session.query(Subscription)
            .filter(
                Subscription.next_run_date == DELIVERY_DATE,
                Subscription.default_address_id.is_(None),
            )
            .all()
        )

        for s in due_subs:
            addr = (
                session.query(Address)
                .filter(Address.user_id == s.user_id)
                .first()
            )
            if not addr:
                addr = get_or_create(
                    session,
                    Address,
                    lookup={"user_id": s.user_id},
                    base={"user_id": s.user_id},
                )
            s.default_address_id = addr.id

        session.commit()

    print("[seed] done")
    print(f"[seed] delivery_date={DELIVERY_DATE}")


if __name__ == "__main__":
    main()

