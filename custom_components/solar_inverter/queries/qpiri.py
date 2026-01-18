from .metric import Metric

from homeassistant.components.sensor import (
    SensorDeviceClass
)


class QPIRI:
    @staticmethod
    def cmd() -> str:
        return "QPIRI"
    
    @staticmethod
    def metrics() -> list[Metric]:
        return [
            Metric(16, "output_source_priority", "Source Priority", SensorDeviceClass.ENUM, None, None)
        ]
    

    @staticmethod
    def parse(parts) -> dict:                 
        measurements = {}

        src_metric = QPIRI.metrics()[0]

        if len(parts) > src_metric.ndx:
            try:
                measurements[src_metric.uuid] = int(parts[src_metric.ndx])
            except Exception:
                pass

        return measurements