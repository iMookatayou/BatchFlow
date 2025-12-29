from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db_session
from app.services.unit_of_work import UnitOfWork
from app.infrastructure.db.models.delivery_batch import DeliveryBatch

router = APIRouter(prefix="/delivery-batches", tags=["delivery_batches"])


def _uow(db: Session) -> UnitOfWork:
    return UnitOfWork(session=db)


@router.get("")
def list_batches(db: Session = Depends(get_db_session)) -> dict:
    uow = _uow(db)

    with uow:
        batches = (
            uow.session.execute(
                select(DeliveryBatch)
                .order_by(DeliveryBatch.delivery_date.desc())
            )
            .scalars()
            .all()
        )

        return {
            "data": [
                {
                    "id": b.id,
                    "public_id": b.public_id,
                    "batch_code": b.batch_code,
                    "delivery_date": b.delivery_date,
                    "zone_id": b.zone_id,
                    "status": int(b.status),
                    "cutoff_at": b.cutoff_at,
                    "locked_at": b.locked_at,
                    "created_at": b.created_at,
                }
                for b in batches
            ]
        }


@router.get("/{batch_id}")
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db_session),
) -> dict:
    uow = _uow(db)

    with uow:
        batch = (
            uow.session.execute(
                select(DeliveryBatch).where(DeliveryBatch.id == batch_id)
            )
            .scalar_one_or_none()
        )

        if not batch:
            raise HTTPException(status_code=404, detail={"code": "BATCH_NOT_FOUND"})

        return {
            "id": batch.id,
            "public_id": batch.public_id,
            "batch_code": batch.batch_code,
            "delivery_date": batch.delivery_date,
            "zone_id": batch.zone_id,
            "status": int(batch.status),
            "cutoff_at": batch.cutoff_at,
            "locked_at": batch.locked_at,
            "orders_count": len(batch.order_links or []),
            "created_at": batch.created_at,
        }
