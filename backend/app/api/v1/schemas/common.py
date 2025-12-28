from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: Optional[str] = Field(default=None, description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Extra fields for debugging")
