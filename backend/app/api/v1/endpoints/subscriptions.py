from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session

from app.api.v1.schemas.subscription import (
    SubscriptionCreateRequest,
    SubscriptionCreateResponse,
    SubscriptionResponse,
    SubscriptionItemResponse,
    SubscriptionPauseRequest,
)
from app.dependencies import get_db_session
from app.services.unit_of_work import UnitOfWork
from app.infrastructure.db.models.address import Address
from app.infrastructure.db.models.plan import Plan
from app.infrastructure.db.models.product_variant import ProductVariant
from app.infrastructure.db.models.subscription import Subscription
from app.infrastructure.db.models.subscription_item import SubscriptionItem

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# NOTE (IMPORTANT):
# - status เป็น coarse state เท่านั้น
# - source of truth ของ lifecycle คือ paused_at / canceled_at
# - generate_orders ใช้ paused_at / canceled_at เป็นตัวตัดสินใจ
SUBSCRIPTION_STATUS_ACTIVE = 1


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
    """
    Helper เพื่อให้ API ใช้ UnitOfWork เหมือน jobs / services
    """
    return UnitOfWork(session=db)


def _require_subscription_owned(uow: UnitOfWork, subscription_id: int, user_id: int) -> Subscription:
    sub = (
        uow.session.execute(
            select(Subscription)
            .where(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id,
            )
            .options(selectinload(Subscription.items))
        )
        .scalar_one_or_none()
    )

    if not sub or sub.deleted_at is not None:
        raise HTTPException(status_code=404, detail={"code": "SUBSCRIPTION_NOT_FOUND"})
    return sub


def _to_subscription_response(sub: Subscription) -> SubscriptionResponse:
    return SubscriptionResponse(
        id=sub.id,
        public_id=sub.public_id,
        user_id=sub.user_id,
        plan_id=sub.plan_id,
        status=int(sub.status),
        start_date=sub.start_date,
        next_run_date=sub.next_run_date,
        end_date=sub.end_date,
        timezone=sub.timezone,
        default_address_id=sub.default_address_id,
        paused_at=sub.paused_at,
        canceled_at=sub.canceled_at,
        deleted_at=sub.deleted_at,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
        items=[
            SubscriptionItemResponse(
                id=it.id,
                variant_id=it.variant_id,
                quantity=int(it.quantity),
                unit_amount=int(it.unit_amount),
                currency=it.currency,
                is_active=int(it.is_active),
            )
            for it in (sub.items or [])
        ],
    )


@router.post("", response_model=SubscriptionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    payload: SubscriptionCreateRequest,
    db: Session = Depends(get_db_session),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> SubscriptionCreateResponse:
    user_id = _require_user_id(x_user_id)
    uow = _uow(db)

    with uow:
        # 1) Validate plan exists + active
        plan = uow.session.execute(
            select(Plan).where(Plan.id == payload.plan_id)
        ).scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=404, detail={"code": "PLAN_NOT_FOUND"})
        if int(plan.is_active) != 1:
            raise HTTPException(status_code=400, detail={"code": "PLAN_INACTIVE"})

        # 2) Validate address ownership
        addr = uow.session.execute(
            select(Address).where(
                Address.id == payload.default_address_id,
                Address.user_id == user_id,
                Address.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if not addr:
            raise HTTPException(status_code=400, detail={"code": "ADDRESS_NOT_OWNED_BY_USER"})

        # 3) Validate variants
        variant_ids = [it.variant_id for it in payload.items]
        variants = uow.session.execute(
            select(ProductVariant).where(
                ProductVariant.id.in_(variant_ids),
                ProductVariant.is_active == 1,
                ProductVariant.deleted_at.is_(None),
            )
        ).scalars().all()
        variant_map = {v.id: v for v in variants}

        missing = [vid for vid in variant_ids if vid not in variant_map]
        if missing:
            raise HTTPException(
                status_code=404,
                detail={"code": "VARIANT_NOT_FOUND", "missing_variant_ids": missing},
            )

        # 4) Enforce pricing (contract price)
        for it in payload.items:
            if it.currency.upper() != "THB":
                raise HTTPException(status_code=400, detail={"code": "UNSUPPORTED_CURRENCY"})

        now = datetime.utcnow()

        sub = Subscription(
            public_id=None,
            user_id=user_id,
            plan_id=payload.plan_id,
            status=SUBSCRIPTION_STATUS_ACTIVE,
            start_date=payload.start_date,
            next_run_date=payload.start_date,
            end_date=None,
            timezone="Asia/Bangkok",
            default_address_id=payload.default_address_id,
            paused_at=None,
            canceled_at=None,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        )
        uow.session.add(sub)
        uow.session.flush()

        for it in payload.items:
            uow.session.add(
                SubscriptionItem(
                    subscription_id=sub.id,
                    variant_id=it.variant_id,
                    quantity=int(it.quantity),
                    unit_amount=int(it.unit_amount),
                    currency=it.currency.upper(),
                    is_active=1,
                    created_at=now,
                    updated_at=now,
                )
            )

    return SubscriptionCreateResponse(
        id=sub.id,
        public_id=sub.public_id,
        user_id=sub.user_id,
        plan_id=sub.plan_id,
        status=int(sub.status),
        start_date=sub.start_date,
        next_run_date=sub.next_run_date,
        default_address_id=sub.default_address_id,
    )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db_session),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> SubscriptionResponse:
    user_id = _require_user_id(x_user_id)
    uow = _uow(db)

    with uow:
        sub = _require_subscription_owned(uow, subscription_id, user_id)
        return _to_subscription_response(sub)


@router.post("/{subscription_id}/pause", response_model=SubscriptionResponse)
def pause_subscription(
    subscription_id: int,
    payload: SubscriptionPauseRequest,
    db: Session = Depends(get_db_session),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> SubscriptionResponse:
    user_id = _require_user_id(x_user_id)
    uow = _uow(db)

    with uow:
        sub = _require_subscription_owned(uow, subscription_id, user_id)

        if sub.canceled_at is not None:
            raise HTTPException(status_code=400, detail={"code": "SUBSCRIPTION_ALREADY_CANCELED"})

        if sub.paused_at is None:
            now = datetime.utcnow()
            sub.paused_at = now
            sub.updated_at = now

        return _to_subscription_response(sub)


@router.post("/{subscription_id}/resume", response_model=SubscriptionResponse)
def resume_subscription(
    subscription_id: int,
    db: Session = Depends(get_db_session),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> SubscriptionResponse:
    user_id = _require_user_id(x_user_id)
    uow = _uow(db)

    with uow:
        sub = _require_subscription_owned(uow, subscription_id, user_id)

        if sub.canceled_at is not None:
            raise HTTPException(status_code=400, detail={"code": "SUBSCRIPTION_ALREADY_CANCELED"})

        if sub.paused_at is not None:
            sub.paused_at = None
            sub.updated_at = datetime.utcnow()

        return _to_subscription_response(sub)


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(
    subscription_id: int,
    db: Session = Depends(get_db_session),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> SubscriptionResponse:
    user_id = _require_user_id(x_user_id)
    uow = _uow(db)

    with uow:
        sub = _require_subscription_owned(uow, subscription_id, user_id)

        if sub.canceled_at is None:
            now = datetime.utcnow()
            sub.canceled_at = now
            sub.paused_at = None
            sub.updated_at = now

        return _to_subscription_response(sub)
