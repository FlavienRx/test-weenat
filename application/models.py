from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from .enumerations import Label


class Datalogguer(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    measurements: list["Measurement"] = Relationship(
        back_populates="datalogguer"
    )


class Measurement(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    datalogguer_id: int = Field(foreign_key="datalogguer.id")
    datalogguer: Datalogguer = Relationship(back_populates="measurements")
    measured_at: datetime
    temperature: float | None = Field(default=None)
    humidity: float | None = Field(default=None)
    precipitation: float | None = Field(default=None)

    __table_args__ = (UniqueConstraint("datalogguer_id", "measured_at"),)


class DataRecordResponse(SQLModel, table=False):
    label: Label
    measured_at: datetime
    value: float | None


class DataRecordAggregateResponse(SQLModel, table=False):
    label: Label
    time_slot: datetime | str
    value: float | None
