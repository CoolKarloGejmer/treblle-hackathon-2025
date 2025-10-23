"""Simple pytest to verify the database session can be created.

Run from the project root (hackathon-backend) so the `app` package is importable:

	venv\Scripts\activate
	pytest app/tests/test_database.py -q

"""

from app.database import SessionLocal, engine, Base


def test_session_creation_and_close():
	# Create tables (no-op if models are not defined yet)
	Base.metadata.create_all(bind=engine)

	db = SessionLocal()
	try:
		assert db is not None
	finally:
		db.close()