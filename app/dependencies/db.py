from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
