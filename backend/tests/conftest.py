# tests/conftest.py
import os
import pytest

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.services.unit_of_work import UnitOfWork


# โหลด .env อัตโนมัติ (ถ้ามี) เพื่อให้ pytest เจอ DATABASE_URL
load_dotenv()


@pytest.fixture(scope="session")
def engine():
    db_url = os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL is required for tests"

    return create_engine(db_url, future=True, pool_pre_ping=True)


@pytest.fixture()
def db_session(engine):
    connection = engine.connect()
    trans = connection.begin()

    SessionLocal = sessionmaker(bind=connection, future=True)
    session = SessionLocal()

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, transaction):
        if transaction.nested and not connection.closed:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture()
def uow_factory(db_session):
    def _factory():
        return UnitOfWork(session=db_session)

    return _factory
