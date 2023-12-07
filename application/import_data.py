from datetime import datetime

import httpx

from .crud import get_or_create_datalogguer, get_or_create_measurement
from .settings import settings


def main():
    response = httpx.get(f"{settings.DATA_APP_BASE_URL}/measurements")

    datas = response.json()

    for id, data in enumerate(datas):
        datalogguer = get_or_create_datalogguer(id)

        for key, values in data.items():
            values["measured_at"] = datetime.fromtimestamp(int(key[:-3]))
            values["datalogguer_id"] = datalogguer.id
            values["precipitation"] = values.pop("precip")
            values["temperature"] = values.pop("temp")
            values["humidity"] = values.pop("hum")

            get_or_create_measurement(values)


if __name__ == "__main__":
    main()
