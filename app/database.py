"""
Database configuration module.
Handles SQLite database initialization and session management for the FastAPI application.
Uses SQLAlchemy as ORM(Object-Relational Mapping) with multi-thread support for development.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Enable multi-threading for FastAPI's ASGI server
# Required because FastAPI handles requests asynchronously
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency function that manages database sessions.
    Yields a SQLAlchemy session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()