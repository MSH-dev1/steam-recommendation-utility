"""Database connection: engine, session factory, base model class."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models (models are added in step 2)."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a session and guarantees it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
