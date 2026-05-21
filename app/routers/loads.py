from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Load
from app.dependencies.auth import verify_api_key
from app.dependencies.db import get_db_session
from app.schemas.loads import LoadOut, LoadsSearchResponse

router = APIRouter(tags=["loads"])


@router.get(
    "/loads-search",
    response_model=LoadsSearchResponse,
    dependencies=[Depends(verify_api_key)],
)
def loads_search(
    reference_number: str = Query(..., min_length=1, description="Load reference number from posting"),
    db: Session = Depends(get_db_session),
) -> LoadsSearchResponse:
    normalized = reference_number.strip()
    matches = (
        db.query(Load)
        .filter(func.lower(Load.reference_number) == normalized.lower())
        .all()
    )
    loads = [LoadOut.model_validate(row) for row in matches]
    return LoadsSearchResponse(
        reference_number=normalized,
        loads=loads,
        count=len(loads),
    )
