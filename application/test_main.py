from urllib.parse import quote_plus
from datetime import datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from .database import get_session
from .main import app
from .models import Datalogguer, Measurement
from .enumerations import Label


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


@pytest.fixture
def setup_db(session: Session):
    for i in range(2):
        datalogguer = Datalogguer(id=i)
        session.add(datalogguer)
        session.commit()

        nb_measure = 5

        for i in range(nb_measure):
            measure = Measurement(
                datalogguer_id=datalogguer.id,
                measured_at=datetime.now() - timedelta(hours=nb_measure - i),
                temperature=i,
                humidity=i,
                precipitation=i,
            )
            session.add(measure)
            session.commit()


def test_create_measure_with_none_value(session: Session):
    datalogguer = Datalogguer(id=0)
    session.add(datalogguer)
    session.commit()

    measure = Measurement(
        datalogguer_id=datalogguer.id,
        measured_at=datetime.now(),
        temperature=None,
        humidity=None,
        precipitation=None,
    )
    session.add(measure)
    session.commit()

    session.refresh(measure)

    assert measure.temperature is None
    assert measure.humidity is None
    assert measure.precipitation is None


@pytest.mark.usefixtures("setup_db")
def test_fetch_raw_data_without_query_param(client: TestClient):
    response = client.get("/api/data")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("setup_db")
def test_fetch_all_raw_data(client: TestClient):
    now = datetime.now()

    before = now.strftime("%Y-%m-%dT%H:%M:%S")
    since = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")

    before = quote_plus(before)
    since = quote_plus(since)

    response = client.get(
        f"/api/data?datalogger=0&since={since}&before={before}"
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 15  # nb_measure * 3


@pytest.mark.usefixtures("setup_db")
def test_fetch_some_raw_data(client: TestClient):
    now = datetime.now()

    before = now.strftime("%Y-%m-%dT%H:%M:%S")
    since = (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")

    before = quote_plus(before)
    since = quote_plus(since)

    response = client.get(
        f"/api/data?datalogger=0&since={since}&before={before}"
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 9  # 3 last measure * 3


@pytest.mark.usefixtures("setup_db")
def test_fetch_aggregate_data_without_query_param(client: TestClient):
    response = client.get("/api/summary")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("setup_db")
def test_fetch_all_aggregate_data(client: TestClient):
    now = datetime.now()

    before = now.strftime("%Y-%m-%dT%H:%M:%S")
    since = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")

    before = quote_plus(before)
    since = quote_plus(since)

    response = client.get(
        f"/api/summary?datalogger=0&since={since}&before={before}"
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 15  # nb_measure * 3


@pytest.mark.usefixtures("setup_db")
def test_fetch_some_aggregate_data(client: TestClient):
    now = datetime.now()

    before = now.strftime("%Y-%m-%dT%H:%M:%S")
    since = (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")

    before = quote_plus(before)
    since = quote_plus(since)

    response = client.get(
        f"/api/summary?datalogger=0&since={since}&before={before}"
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 9  # 3 last measure * 3


@pytest.mark.usefixtures("setup_db")
def test_fetch_max_aggregate_data(client: TestClient):
    now = datetime.now()

    before = now.strftime("%Y-%m-%dT%H:%M:%S")
    since = (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")

    before = quote_plus(before)
    since = quote_plus(since)

    response = client.get(
        f"/api/summary?datalogger=0&since={since}&before={before}&span=max"
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    for item in data:
        assert item["value"] == 4.0

@pytest.mark.usefixtures("setup_db")
def test_fetch_day_aggregate_data(client: TestClient):
    now = datetime.now()

    before = now.strftime("%Y-%m-%dT%H:%M:%S")
    since = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")

    before = quote_plus(before)
    since = quote_plus(since)

    response = client.get(
        f"/api/summary?datalogger=0&since={since}&before={before}&span=day"
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    aggregate_data = {
        Label.temperature_min: 0,
        Label.temperature_max: 4,
        Label.temperature_avg: 2,
        Label.humidity_min: 0,
        Label.humidity_max: 4,
        Label.humidity_avg: 2,
        Label.precipitation_sum: 10,
    }

    for i, (label, value) in enumerate(aggregate_data.items()):
        assert data[i]["label"] == label.value
        assert data[i]["value"] == value
