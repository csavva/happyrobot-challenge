from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Load(Base):
    __tablename__ = "loads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    load_id: Mapped[str] = mapped_column(String(64))
    origin: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    pickup_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    delivery_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    equipment_type: Mapped[str] = mapped_column(String(64))
    loadboard_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[int] = mapped_column(Integer)
    commodity_type: Mapped[str] = mapped_column(String(128))
    num_of_pieces: Mapped[int] = mapped_column(Integer)
    miles: Mapped[int] = mapped_column(Integer)
    dimensions: Mapped[str | None] = mapped_column(String(128), nullable=True)
