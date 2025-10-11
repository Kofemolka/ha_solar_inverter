from .metric import Metric

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfElectricCurrent,
    UnitOfFrequency,
    UnitOfApparentPower
)


class QPIGS:
    @staticmethod
    def cmd() -> str:
        return "QPIGS"
    
    @staticmethod
    def metrics() -> list[Metric]:
        return [
            Metric(0, "grid_voltage", "Grid Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, SensorStateClass.MEASUREMENT)
        ]
    
    @staticmethod
    def parse(parts) -> dict:       
        def f(i):
            try:
                return float(parts[i])
            except Exception:
                return None
                
        measurements = {}

        for metric in QPIGS.metrics():
            measurements[metric.uuid] = f(metric.ndx)

        return measurements
    
        return {
            "grid_voltage": f(0),
            "grid_freq": f(1),
            "ac_output_voltage": f(2),
            "ac_output_freq": f(3),
            "load_va": f(4),
            "load_watt": f(5),
            "load_pcnt": f(6),
            "pv_voltage": f(7),
            "battery_voltage": f(8),
            "battery_charge_current": f(9),
            'battery_level': f(10),
            'temperature': f(11),
            'pv_input_current': f(12),
            'pv_input_voltage': f(13),
            'battery_discharge_current': f(15),
            'pv_input_watt': f(19)
        }