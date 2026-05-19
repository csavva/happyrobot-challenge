from fastapi import APIRouter, HTTPException, Query

from app.schemas.fmcsa import FMCSAValidateResponse
from app.services.fmcsa import FMCSAError, validate_mc_number

router = APIRouter(tags=["fmcsa"])


@router.get("/fmcsa-validate", response_model=FMCSAValidateResponse)
def fmcsa_validate(
    mc_number: str = Query(..., min_length=1, description="Motor carrier MC number"),
) -> FMCSAValidateResponse:
    try:
        return validate_mc_number(mc_number)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FMCSAError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
