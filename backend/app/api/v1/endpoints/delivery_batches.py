from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/delivery-batches", tags=["delivery_batches"])


@router.get("")
def list_batches() -> dict:
    # TODO: implement when batch rules are finalized
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"code": "NOT_IMPLEMENTED"})


@router.get("/{batch_id}")
def get_batch(batch_id: int) -> dict:
    # TODO: implement when batch rules are finalized
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"code": "NOT_IMPLEMENTED"})
