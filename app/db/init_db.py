from sqlalchemy import text

from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.seed.seed_calls import seed_calls_if_empty
from app.seed.seed_loads import seed_loads_if_empty


def _migrate_calls_schema() -> None:
    if engine is None:
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE calls ADD COLUMN IF NOT EXISTS "
                "call_sentiment VARCHAR(16) NOT NULL DEFAULT 'Neutral'"
            )
        )


def init_database() -> None:
    if engine is None or SessionLocal is None:
        return

    Base.metadata.create_all(bind=engine)
    _migrate_calls_schema()

    db = SessionLocal()
    try:
        seed_loads_if_empty(db)
        seed_calls_if_empty(db)
    finally:
        db.close()
