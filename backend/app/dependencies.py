from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.settings import settings

_engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_db_session() -> Generator[Session, None, None]:
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
