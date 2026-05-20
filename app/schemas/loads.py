from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class LoadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference_number: str
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: Decimal
    notes: str | None
    weight: int
    commodity_type: str
    num_of_pieces: int
    miles: int
    dimensions: str | None


class LoadsSearchResponse(BaseModel):
    reference_number: str
    loads: list[LoadOut]
    count: int
