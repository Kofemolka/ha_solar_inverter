from .metric import Metric

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)


class QMOD:
    @staticmethod
    def cmd() -> str:
        return "QMOD"
    
    @staticmethod
    def metrics() -> list[Metric]:
        return [
            Metric(0, "mode", "Mode", SensorDeviceClass.ENUM, "", SensorStateClass.MEASUREMENT)
        ]
    
    @staticmethod
    def parse(parts) -> dict:                      
        measurements = {}

        if len(parts) > 0:
            measurements[QMOD.metrics()[0].uuid] = parts[0]

        return measurements