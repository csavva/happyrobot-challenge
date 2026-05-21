from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Classification = Literal["Success", "Rate too high", "Not interested"]
BookingDecision = Literal["yes", "no"]


class CallCreate(BaseModel):
    classification: Classification
    reference_number: str = Field(..., min_length=1)
    mc_number: str = Field(..., min_length=1)
    decline_reason: str = ""
    booking_decision: BookingDecision
    call_duration: int = 0

    @field_validator("reference_number", "mc_number", "decline_reason", mode="before")
    @classmethod
    def strip_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("call_duration", mode="before")
    @classmethod
    def parse_duration(cls, value: object) -> int:
        if isinstance(value, int):
            return max(0, value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return 0
            return max(0, int(stripped))
        raise ValueError("call_duration must be a number or numeric string")

    @model_validator(mode="after")
    def validate_consistency(self) -> Self:
        if self.classification == "Success" and self.booking_decision != "yes":
            raise ValueError("classification 'Success' requires booking_decision 'yes'")
        if self.classification in ("Rate too high", "Not interested") and self.booking_decision != "no":
            raise ValueError(
                f"classification '{self.classification}' requires booking_decision 'no'"
            )
        return self


class CallOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    classification: str
    reference_number: str
    mc_number: str
    decline_reason: str | None
    booking_decision: str
    call_duration_seconds: int
    created_at: datetime


class CallAnalyticsSummary(BaseModel):
    total_calls: int
    success_rate_percent: float
    by_classification: dict[str, int]
    booking_yes: int
    booking_no: int
    avg_call_duration_seconds: float


class CallAnalyticsResponse(BaseModel):
    summary: CallAnalyticsSummary
    recent_calls: list[CallOut]
