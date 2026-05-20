from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.seed.seed_loads import seed_loads_if_empty


def init_database() -> None:
    if engine is None or SessionLocal is None:
        return

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_loads_if_empty(db)
    finally:
        db.close()
