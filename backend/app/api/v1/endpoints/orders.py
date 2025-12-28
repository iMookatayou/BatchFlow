from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def list_orders() -> dict:
    # TODO: implement when business requirements are confirmed
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"code": "NOT_IMPLEMENTED"})


@router.get("/{order_id}")
def get_order(order_id: int) -> dict:
    # TODO: implement when business requirements are confirmed
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"code": "NOT_IMPLEMENTED"})
