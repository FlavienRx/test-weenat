from enum import Enum


class Span(str, Enum):
    day = "day"
    hour = "hour"
    max = "max"


class Label(str, Enum):
    temperature = "Temperature"
    temperature_min = "Temperature min"
    temperature_max = "Temperature max"
    temperature_avg = "Temperature avg"
    humidity = "Humidity"
    humidity_min = "Humidity min"
    humidity_max = "Humidity max"
    humidity_avg = "Humidity avg"
    precipitation = "Precipitation"
    precipitation_max = "Precipitation max"
    precipitation_sum = "Precipitation sum"
