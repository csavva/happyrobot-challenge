from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models import Call
from app.dependencies.auth import verify_api_key
from app.dependencies.db import get_db_session
from app.schemas.calls import CallCreate, CallOut
from app.services.fmcsa import normalize_mc_number

router = APIRouter(tags=["calls"])


def _empty_to_none(value: str) -> str | None:
    return value if value else None


@router.post(
    "/calls",
    response_model=CallOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
def create_call(payload: CallCreate, db: Session = Depends(get_db_session)) -> Call:
    call = Call(
        classification=payload.classification,
        reference_number=payload.reference_number,
        mc_number=normalize_mc_number(payload.mc_number),
        decline_reason=_empty_to_none(payload.decline_reason),
        booking_decision=payload.booking_decision,
        call_sentiment=payload.call_sentiment,
        call_duration_seconds=payload.call_duration,
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call
