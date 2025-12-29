from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session

from app.dependencies import get_db_session
from app.services.unit_of_work import UnitOfWork
from app.infrastructure.db.models.order import Order
from app.infrastructure.db.models.order_item import OrderItem

router = APIRouter(prefix="/orders", tags=["orders"])


def _require_user_id(x_user_id: Optional[str]) -> int:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing X-User-Id"},
        )
    try:
        uid = int(x_user_id)
        if uid <= 0:
            raise ValueError
        return uid
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid X-User-Id"},
        )


def _uow(db: Session) -> UnitOfWork:
    return UnitOfWork(session=db)


@router.get("")
def list_orders(
    db: Session = Depends(get_db_session),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> dict:
    user_id = _require_user_id(x_user_id)
    uow = _uow(db)

    with uow:
        orders = (
            uow.session.execute(
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
            )
            .scalars()
            .all()
        )

        return {
            "data": [
                {
                    "id": o.id,
                    "public_id": o.public_id,
                    "order_no": o.order_no,
                    "subscription_id": o.subscription_id,
                    "status": int(o.status),
                    "delivery_date": o.delivery_date,
                    "currency": o.currency,
                    "subtotal_amount": int(o.subtotal_amount),
                    "shipping_amount": int(o.shipping_amount),
                    "total_amount": int(o.total_amount),
                    "created_at": o.created_at,
                }
                for o in orders
            ]
        }


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db_session),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> dict:
    user_id = _require_user_id(x_user_id)
    uow = _uow(db)

    with uow:
        order = (
            uow.session.execute(
                select(Order)
                .where(
                    Order.id == order_id,
                    Order.user_id == user_id,
                )
                .options(selectinload(Order.items))
            )
            .scalar_one_or_none()
        )

        if not order:
            raise HTTPException(status_code=404, detail={"code": "ORDER_NOT_FOUND"})

        return {
            "id": order.id,
            "public_id": order.public_id,
            "order_no": order.order_no,
            "subscription_id": order.subscription_id,
            "status": int(order.status),
            "delivery_date": order.delivery_date,
            "currency": order.currency,
            "subtotal_amount": int(order.subtotal_amount),
            "shipping_amount": int(order.shipping_amount),
            "total_amount": int(order.total_amount),
            "items": [
                {
                    "id": it.id,
                    "variant_id": it.variant_id,
                    "sku": it.sku,
                    "name": it.name,
                    "quantity": int(it.quantity),
                    "unit_amount": int(it.unit_amount),
                    "line_total_amount": int(it.line_total_amount),
                }
                for it in (order.items or [])
            ],
            "created_at": order.created_at,
        }
