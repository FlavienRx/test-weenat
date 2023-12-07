from sqlmodel import select

from .database import get_session
from .models import Datalogguer, Measurement

session = next(get_session())


def get_or_create_datalogguer(id: int):
    datalogguer = session.get(Datalogguer, id)

    if not datalogguer:
        datalogguer = Datalogguer(id=id)
        session.add(datalogguer)
        session.commit()

        session.refresh(datalogguer)

    return datalogguer


def get_or_create_measurement(values: dict):
    statement = select(Measurement).where(
        Measurement.measured_at == values["measured_at"],
    )

    measurement = session.exec(statement).first()

    if not measurement:
        measurement = Measurement(**values)
        session.add(measurement)
        session.commit()

        session.refresh(measurement)

    return measurement
