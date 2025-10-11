from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)


@dataclass
class Metric:
    ndx: int
    uuid: str
    name: str
    dc: SensorDeviceClass
    uom: str
    sc: SensorStateClass