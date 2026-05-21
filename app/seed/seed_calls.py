import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import Call
from app.schemas.calls import CallCreate
from app.services.fmcsa import normalize_mc_number

CALLS_FILE = Path(__file__).parent / "calls.json"


def _empty_to_none(value: str) -> str | None:
    return value if value else None


def seed_calls_if_empty(db: Session) -> int:
    if db.query(Call).count() > 0:
        return 0

    with CALLS_FILE.open(encoding="utf-8") as f:
        records = json.load(f)

    for record in records:
        payload = CallCreate.model_validate(record)
        db.add(
            Call(
                classification=payload.classification,
                reference_number=payload.reference_number,
                mc_number=normalize_mc_number(payload.mc_number),
                decline_reason=_empty_to_none(payload.decline_reason),
                booking_decision=payload.booking_decision,
                call_duration_seconds=payload.call_duration,
            )
        )

    db.commit()
    return len(records)
