"""
Database Connection
SQLAlchemy setup and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from database.models import Base
from utils.logger import get_logger

logger = get_logger(__name__)

# Database URL - defaults to SQLite, can be overridden with environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./combo_optimizer.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (for non-FastAPI usage)
    
    Usage:
        db = get_db_session()
        try:
            # use db
        finally:
            db.close()
    """
    return SessionLocal()

