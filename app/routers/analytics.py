from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db_session
from app.schemas.calls import CallAnalyticsResponse
from app.services.analytics import get_call_analytics

router = APIRouter(tags=["analytics"])


@router.get("/analytics/calls", response_model=CallAnalyticsResponse)
def call_analytics(db: Session = Depends(get_db_session)) -> CallAnalyticsResponse:
    return get_call_analytics(db)
