# app/shared/model_fields.py
from __future__ import annotations

from typing import Any, Iterable
from sqlalchemy.inspection import inspect as sa_inspect


def pick_attr(model: type, candidates: Iterable[str]) -> str:
    """
    Return the first attribute name that exists on the SQLAlchemy model.
    Raise ValueError if none found.
    """
    mapper = sa_inspect(model)
    cols = {c.key for c in mapper.columns}
    rels = set(mapper.relationships.keys())
    props = cols | rels | set(dir(model))

    for name in candidates:
        if name in props:
            return name
    raise ValueError(f"Cannot find any of {list(candidates)} on model={model.__name__}")


def enum_values(model: type, field_name: str) -> list[Any]:
    """
    Try to retrieve allowed enum values from an Enum column if present.
    Returns [] if not an Enum.
    """
    mapper = sa_inspect(model)
    col = mapper.columns.get(field_name)
    if col is None:
        return []
    typ = getattr(col, "type", None)
    # SQLAlchemy Enum has .enums (list[str]) in many cases
    vals = getattr(typ, "enums", None)
    return list(vals) if vals else []
