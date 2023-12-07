from datetime import datetime, timedelta
from typing import Annotated

import numpy as np
from fastapi import Depends, Query
from sqlmodel import select

from .database import Session, get_session
from .enumerations import Label
from .models import DataRecordAggregateResponse, DataRecordResponse, Measurement


def common_parameters(
    datalogger: Annotated[int, Query(ge=0, le=1)],
    since: datetime = datetime(year=2021, month=1, day=1),
    before: datetime = datetime.now(),
    session: Session = Depends(get_session),
) -> list:
    return [datalogger, since, before, session]


def get_measurements(
    commons: Annotated[list, Depends(common_parameters)]
) -> list[Measurement]:
    datalogger, since, before, session = commons

    statement = select(Measurement).where(
        Measurement.datalogguer_id == datalogger,
        Measurement.measured_at > since,
        Measurement.measured_at < before,
    )

    return session.exec(statement).all()


def get_raw_data(
    commons: Annotated[list, Depends(common_parameters)],
    data_structure: DataRecordResponse | DataRecordAggregateResponse
) -> list[DataRecordResponse]:
    data = []

    for measure in get_measurements(commons):
        for attr in ["temperature", "humidity", "precipitation"]:
            if data_structure is DataRecordResponse:
                new_data = data_structure(
                    label=getattr(Label, attr).value,
                    measured_at=measure.measured_at,
                    value=getattr(measure, attr),
                )
            else:
                new_data = data_structure(
                    label=getattr(Label, attr).value,
                    time_slot=measure.measured_at,
                    value=getattr(measure, attr),
                )
            
            data.append(new_data)

    return data


def get_aggregate_data(
    commons: Annotated[list, Depends(common_parameters)],
    delta: timedelta | None,
) -> list[DataRecordAggregateResponse]:
    _, since, before, _ = commons
    data = []

    if delta:
        step: datetime = since + delta

    else:
        step = before

    while step <= before:
        measurements = get_measurements(commons)

        if measurements:
            span_datas = [
                [measure.temperature, measure.humidity, measure.precipitation]
                for measure in measurements
            ]

            # Replace None value by np.nan
            span_datas = np.array(span_datas, dtype=float)

            if delta:
                temp_min, hum_min, _ = np.nanmin(span_datas, axis=0)
                temp_max, hum_max, _ = np.nanmax(span_datas, axis=0)
                temp_avg, hum_avg, _ = np.nanmean(span_datas, axis=0)
                _, _, precip_sum = np.nansum(span_datas, axis=0)

                aggregate_data = {
                    Label.temperature_min: temp_min,
                    Label.temperature_max: temp_max,
                    Label.temperature_avg: temp_avg,
                    Label.humidity_min: hum_min,
                    Label.humidity_max: hum_max,
                    Label.humidity_avg: hum_avg,
                    Label.precipitation_sum: precip_sum,
                }

            else:
                temp_max, hum_max, precip_max = np.nanmax(span_datas, axis=0)

                aggregate_data = {
                    Label.temperature_max: temp_max,
                    Label.humidity_max: hum_max,
                    Label.precipitation_max: precip_max,
                }

            time_slot = f"{since}, {step}"

            for label, value in aggregate_data.items():
                data.append(
                    DataRecordAggregateResponse(
                        label=label.value,
                        time_slot=time_slot,
                        value=value,
                    )
                )

        since = step
        step = since + timedelta(hours=1)

    return data
