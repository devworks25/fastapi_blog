import logging
import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER", "fastapi_user"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "fastapi_blog"),
)
engine = create_engine(database_url, pool_pre_ping=True, connect_args={"connect_timeout": 5})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@contextmanager
def managed_db_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()