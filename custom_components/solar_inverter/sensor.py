from __future__ import annotations
from dataclasses import dataclass
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import UnitOfElectricPotential, UnitOfPower, UnitOfElectricCurrent, UnitOfFrequency
from .const import DOMAIN


SENSOR_MAP = {
    # key -> (name, unit)
    "grid_voltage": ("Grid Voltage", UnitOfElectricPotential.VOLT),
    "grid_freq": ("Grid Frequency", UnitOfFrequency.HERTZ),
    "ac_output_voltage": ("AC Output Voltage", UnitOfElectricPotential.VOLT),
    "ac_output_freq": ("AC Output Frequency", UnitOfFrequency.HERTZ),
    "ac_output_va": ("AC Output Apparent Power", UnitOfPower.VOLT_AMPERE),
    "ac_output_w": ("AC Output Active Power", UnitOfPower.WATT),
    "ac_output_percent": ("AC Output Load %", "%"),
    "bus_voltage": ("Bus Voltage", UnitOfElectricPotential.VOLT),
    "battery_voltage": ("Battery Voltage", UnitOfElectricPotential.VOLT),
    "battery_charge_current": ("Battery Charge Current", UnitOfElectricCurrent.AMPERE),
}

async def async_setup_platform(hass: HomeAssistant, config: ConfigType, async_add_entities, discovery_info=None):
    data = hass.data[DOMAIN]
    name = data["name"]
    coordinator = data["coordinator"]


    entities = []
    # QPIGS-derived metrics
    for key, (friendly, unit) in SENSOR_MAP.items():
        entities.append(HidInverterNumberSensor(coordinator, f"{name} {friendly}", key))


    # Raw text helpers for debug / development
    for q in data["queries"]:
        entities.append(HidInverterRawSensor(coordinator, f"{name} {q.upper()} Raw", q))


    async_add_entities(entities)


class _Base(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name: str):
    super().__init__(coordinator)
    self._attr_name = name


    @property
    def available(self) -> bool:
        d = self.coordinator.data or {}
        # available if any query succeeded
        return any(v.get("ok") for v in d.values())


class HidInverterNumberSensor(_Base):
    def __init__(self, coordinator, name: str, field: str):
        super().__init__(coordinator, name)
        self._field = field


    @property
    def native_value(self):
        d = self.coordinator.data or {}
        qpigs = d.get("qpigs", {})
        return qpigs.get(self._field)


class HidInverterRawSensor(_Base):
    def __init__(self, coordinator, name: str, query_key: str):
        super().__init__(coordinator, name)
        self._q = query_key


    @property
    def native_value(self):
        d = self.coordinator.data or {}
        qd = d.get(self._q, {})
        return qd.get("raw")