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
    UnitOfApparentPower,
    UnitOfTemperature,
    PERCENTAGE
)


class QPIGS:
    @staticmethod
    def cmd() -> str:
        return "QPIGS"
    
    @staticmethod
    def metrics() -> list[Metric]:
        return [
            Metric(0, "grid_voltage", "Grid Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, SensorStateClass.MEASUREMENT),
            Metric(1, "grid_freq", "Grid Frequency", SensorDeviceClass.FREQUENCY, UnitOfFrequency.HERTZ, SensorStateClass.MEASUREMENT),
            Metric(2, "ac_output_voltage", "Output Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, SensorStateClass.MEASUREMENT),
            Metric(3, "ac_output_freq", "Output Frequency", SensorDeviceClass.FREQUENCY, UnitOfFrequency.HERTZ, SensorStateClass.MEASUREMENT),
            Metric(4, "load_va", "Load VA", SensorDeviceClass.APPARENT_POWER, UnitOfApparentPower.VOLT_AMPERE, SensorStateClass.MEASUREMENT),
            Metric(5, "load_watt", "Load W", SensorDeviceClass.POWER, UnitOfPower.WATT, SensorStateClass.MEASUREMENT),
            Metric(6, "load_pcnt", "Load %", SensorDeviceClass.POWER_FACTOR, PERCENTAGE, SensorStateClass.MEASUREMENT),
            # TODO: not sure
            Metric(7, "pv_voltage", "PV Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, SensorStateClass.MEASUREMENT), 
            Metric(8, "battery_voltage", "Battery Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, SensorStateClass.MEASUREMENT),
            Metric(9, "battery_charge_current", "Battery Charge Current", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, SensorStateClass.MEASUREMENT),
            Metric(10, "battery_level", "Battery Level", SensorDeviceClass.BATTERY, PERCENTAGE, SensorStateClass.MEASUREMENT),
            Metric(11, "temperature", "Inverter Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT),
            Metric(12, "pv_input_current", "PV Input Current", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, SensorStateClass.MEASUREMENT),
            Metric(13, "pv_input_voltage", "PV Input Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT,  SensorStateClass.MEASUREMENT),
            Metric(15, "battery_discharge_current", "Battery Discharge Current", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, SensorStateClass.MEASUREMENT),
            Metric(19, "pv_input_watt", "PV Input Power", SensorDeviceClass.POWER, UnitOfPower.WATT, SensorStateClass.MEASUREMENT),
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