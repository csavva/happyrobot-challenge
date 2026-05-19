from pydantic import BaseModel, Field


class FMCSAValidateResponse(BaseModel):
    eligible: bool
    mc_number: str
    legal_name: str | None = None
    dba_name: str | None = None
    dot_number: int | None = None
    allow_to_operate: bool | None = None
    out_of_service: bool | None = None
    reason: str | None = None
