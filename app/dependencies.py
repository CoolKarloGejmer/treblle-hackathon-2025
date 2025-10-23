"""Common dependencies for FastAPI endpoints.

Provides `get_db` for obtaining a SQLAlchemy session.
"""

from typing import Generator
from app.database import SessionLocal


def get_db() -> Generator:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
