from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, conint, validator


class SubscriptionItemCreate(BaseModel):
    variant_id: conint(gt=0) = Field(..., description="ProductVariant.id")
    quantity: conint(gt=0) = Field(..., description="Quantity per cycle, must be > 0")
    unit_amount: conint(gt=0) = Field(..., description="Contract unit price (minor units), must be > 0")
    currency: str = Field("THB", min_length=3, max_length=3)

    @validator("currency")
    def _currency_upper(cls, v: str) -> str:
        v = v.upper()
        if len(v) != 3:
            raise ValueError("INVALID_CURRENCY")
        return v

class SubscriptionCreateRequest(BaseModel):
    plan_id: conint(gt=0)
    start_date: date
    default_address_id: conint(gt=0)
    items: List[SubscriptionItemCreate] = Field(..., min_items=1)

    @validator("items")
    def _no_duplicate_variants(cls, items: List[SubscriptionItemCreate]) -> List[SubscriptionItemCreate]:
        seen = set()
        for it in items:
            if it.variant_id in seen:
                raise ValueError("DUPLICATE_VARIANT_IN_ITEMS")
            seen.add(it.variant_id)
        return items

class SubscriptionCreateResponse(BaseModel):
    id: int
    public_id: Optional[str]
    user_id: int
    plan_id: int
    status: int
    start_date: date
    next_run_date: date
    default_address_id: Optional[int]

class SubscriptionItemResponse(BaseModel):
    id: int
    variant_id: int
    quantity: int
    unit_amount: int
    currency: str
    is_active: int

class SubscriptionResponse(BaseModel):
    id: int
    public_id: Optional[str]
    user_id: int
    plan_id: int
    status: int

    start_date: date
    next_run_date: date
    end_date: Optional[date]

    timezone: str
    default_address_id: Optional[int]

    paused_at: Optional[datetime]
    canceled_at: Optional[datetime]
    deleted_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    items: List[SubscriptionItemResponse] = Field(default_factory=list)

class SubscriptionPauseRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=500)
