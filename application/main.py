from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI

from .enumerations import Span
from .models import DataRecordAggregateResponse, DataRecordResponse
from .utils import common_parameters, get_aggregate_data, get_raw_data

app = FastAPI()


@app.get("/api/summary", response_model=list[DataRecordAggregateResponse])
def fetch_aggregate_data(
    commons: Annotated[list, Depends(common_parameters)],
    span: Span = None,
):
    if span is None:
        data = get_raw_data(commons, DataRecordAggregateResponse)

    elif span == Span.day:
        data = get_aggregate_data(commons, timedelta(days=1))

    elif span == Span.hour:
        data = get_aggregate_data(commons, timedelta(hours=1))

    elif span == Span.max:
        data = get_aggregate_data(commons, None)

    return data


@app.get("/api/data", response_model=list[DataRecordResponse])
def fetch_raw_data(
    commons: Annotated[list, Depends(common_parameters)],
):
    return get_raw_data(commons, DataRecordResponse)
