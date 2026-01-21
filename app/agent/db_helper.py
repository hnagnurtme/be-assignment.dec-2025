"""Synchronous database helper for Agent tools.

This module provides sync database sessions for Agent tools to avoid
async event loop conflicts when running in separate threads.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings


# Convert async URL to sync
sync_url = str(settings.database_url).replace('+asyncpg', '')

engine = create_engine(
    sync_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_sync_session() -> Session:
    """Create a synchronous database session for Agent tools.
    
    Returns:
        Session: SQLAlchemy synchronous session
    """
    return SessionLocal()
