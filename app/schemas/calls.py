from datetime import datetime
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Classification = Literal["Success", "Rate too high", "Not interested"]
BookingDecision = Literal["yes", "no"]
CallSentiment = Literal["Positive", "Negative", "Neutral"]


class CallCreate(BaseModel):
    classification: Classification
    reference_number: str = Field(..., min_length=1)
    mc_number: str = Field(..., min_length=1)
    decline_reason: str = ""
    booking_decision: BookingDecision
    call_sentiment: CallSentiment
    call_duration: int = 0
    carrier_initial_offer: float | None = None
    final_agreed_rate: float | None = None
    num_negotiation_rounds: int | None = None

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

    @field_validator("carrier_initial_offer", "final_agreed_rate", mode="before")
    @classmethod
    def parse_optional_float(cls, value: object) -> float | None:
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            return float(stripped)
        raise ValueError("must be a number or numeric string")

    @field_validator("num_negotiation_rounds", mode="before")
    @classmethod
    def parse_optional_int(cls, value: object) -> int | None:
        if value is None or value == "":
            return None
        if isinstance(value, int):
            return max(0, value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            return max(0, int(stripped))
        raise ValueError("num_negotiation_rounds must be a number or numeric string")

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
    call_sentiment: str
    carrier_initial_offer: float | None = None
    final_agreed_rate: float | None = None
    num_negotiation_rounds: int | None = None
    call_duration_seconds: int
    created_at: datetime

    @field_validator("carrier_initial_offer", "final_agreed_rate", mode="before")
    @classmethod
    def decimal_to_float(cls, value: object) -> object:
        if isinstance(value, Decimal):
            return float(value)
        return value


class CallAnalyticsSummary(BaseModel):
    total_calls: int
    success_rate_percent: float
    by_classification: dict[str, int]
    by_sentiment: dict[str, int]
    booking_yes: int
    booking_no: int
    avg_call_duration_seconds: float
    avg_final_rate: float | None
    avg_negotiation_rounds: float | None


class CallAnalyticsResponse(BaseModel):
    summary: CallAnalyticsSummary
    recent_calls: list[CallOut]
