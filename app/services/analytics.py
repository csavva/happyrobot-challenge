from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Call
from app.schemas.calls import CallAnalyticsResponse, CallAnalyticsSummary, CallOut

CLASSIFICATIONS = ("Success", "Rate too high", "Not interested")
RECENT_CALLS_LIMIT = 20


def get_call_analytics(db: Session) -> CallAnalyticsResponse:
    total_calls = db.query(func.count(Call.id)).scalar() or 0

    by_classification: dict[str, int] = {label: 0 for label in CLASSIFICATIONS}
    rows = (
        db.query(Call.classification, func.count(Call.id))
        .group_by(Call.classification)
        .all()
    )
    for classification, count in rows:
        if classification in by_classification:
            by_classification[classification] = count

    booking_yes = (
        db.query(func.count(Call.id)).filter(Call.booking_decision == "yes").scalar() or 0
    )
    booking_no = (
        db.query(func.count(Call.id)).filter(Call.booking_decision == "no").scalar() or 0
    )

    avg_duration = db.query(func.avg(Call.call_duration_seconds)).scalar()
    avg_call_duration_seconds = float(avg_duration) if avg_duration is not None else 0.0

    success_count = by_classification.get("Success", 0)
    success_rate_percent = (
        round(100.0 * success_count / total_calls, 1) if total_calls > 0 else 0.0
    )

    recent = (
        db.query(Call)
        .order_by(Call.created_at.desc())
        .limit(RECENT_CALLS_LIMIT)
        .all()
    )

    return CallAnalyticsResponse(
        summary=CallAnalyticsSummary(
            total_calls=total_calls,
            success_rate_percent=success_rate_percent,
            by_classification=by_classification,
            booking_yes=booking_yes,
            booking_no=booking_no,
            avg_call_duration_seconds=round(avg_call_duration_seconds, 1),
        ),
        recent_calls=[CallOut.model_validate(row) for row in recent],
    )
