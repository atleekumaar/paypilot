"""Database connection and session lifecycle management."""

from contextlib import contextmanager
import logging
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker] = None


def resolve_database_url(url: Optional[str] = None) -> str:
    """Normalize configured database URL for synchronous SQLAlchemy."""
    raw_url = url or get_settings().DATABASE_URL or "sqlite:///./paypilot.db"
    if raw_url.startswith("sqlite+aiosqlite://"):
        return raw_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgresql://") and "+psycopg" not in raw_url:
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


def get_engine(database_url: Optional[str] = None) -> Engine:
    """Obtain or initialize the singleton database engine with appropriate pooling."""
    global _engine, _SessionFactory
    target_url = resolve_database_url(database_url)

    if _engine is not None and str(_engine.url) == target_url:
        return _engine

    is_sqlite = target_url.startswith("sqlite")
    is_in_memory = ":memory:" in target_url or "mode=memory" in target_url

    engine_kwargs = {"echo": getattr(get_settings(), "DB_ECHO", False)}

    if is_sqlite:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        if is_in_memory:
            engine_kwargs["poolclass"] = StaticPool
    else:
        # PostgreSQL / Production settings
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20

    _engine = create_engine(target_url, **engine_kwargs)
    _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_session_factory(database_url: Optional[str] = None) -> sessionmaker:
    """Return configured session factory."""
    global _SessionFactory
    if _SessionFactory is None or (database_url and str(_engine.url) != resolve_database_url(database_url)):
        get_engine(database_url)
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    """FastAPI request-scoped dependency yielding a database session."""
    factory = get_session_factory()
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context(database_url: Optional[str] = None) -> Generator[Session, None, None]:
    """Context manager for explicit transaction boundary and session cleanup outside FastAPI routes."""
    factory = get_session_factory(database_url)
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db(engine: Optional[Engine] = None) -> None:
    """Create all database tables discovered in ORM metadata."""
    eng = engine or get_engine()
    # Import all models to ensure metadata registration
    import app.models  # noqa
    Base.metadata.create_all(bind=eng)
    logger.info("Database initialized successfully.")


def reset_db(engine: Optional[Engine] = None, populate_defaults: bool = True) -> None:
    """Drop and recreate all tables (used for test teardown and clean resets)."""
    eng = engine or get_engine()
    import app.models  # noqa
    Base.metadata.drop_all(bind=eng)
    Base.metadata.create_all(bind=eng)
    if populate_defaults:
        from app.repositories.order_repository import get_order_repository
        from app.repositories.shipment_repository import get_shipment_repository
        from app.services.notification_service import get_notification_service
        get_order_repository().reset_defaults()
        get_shipment_repository().reset_defaults()
        get_notification_service().reset_defaults()

