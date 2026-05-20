import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import Load

LOADS_FILE = Path(__file__).parent / "loads.json"


def seed_loads_if_empty(db: Session) -> int:
    if db.query(Load).count() > 0:
        return 0

    with LOADS_FILE.open(encoding="utf-8") as f:
        records = json.load(f)

    for record in records:
        db.add(
            Load(
                reference_number=record["reference_number"],
                load_id=record["load_id"],
                origin=record["origin"],
                destination=record["destination"],
                pickup_datetime=datetime.fromisoformat(record["pickup_datetime"]),
                delivery_datetime=datetime.fromisoformat(record["delivery_datetime"]),
                equipment_type=record["equipment_type"],
                loadboard_rate=Decimal(str(record["loadboard_rate"])),
                notes=record.get("notes"),
                weight=record["weight"],
                commodity_type=record["commodity_type"],
                num_of_pieces=record["num_of_pieces"],
                miles=record["miles"],
                dimensions=record.get("dimensions"),
            )
        )

    db.commit()
    return len(records)
