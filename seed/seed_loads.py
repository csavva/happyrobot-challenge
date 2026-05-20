"""Run seed against the configured database: python -m seed.seed_loads"""

from app.db.database import SessionLocal, engine
from app.db.init_db import init_database


def main() -> None:
    if engine is None or SessionLocal is None:
        raise SystemExit("DATABASE_URL is not configured")
    init_database()
    print("Database initialized and seed data loaded if empty.")


if __name__ == "__main__":
    main()
