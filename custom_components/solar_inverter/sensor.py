from __future__ import annotations
from dataclasses import dataclass
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import UnitOfElectricPotential, UnitOfPower, UnitOfElectricCurrent, UnitOfFrequency, UnitOfApparentPower
from .const import DOMAIN, CONF_QUERIES
from .queries import get_user_queries, metric

# SENSOR_MAP = {
#     # key -> (name, unit)
#     "grid_voltage": ("Grid Voltage", UnitOfElectricPotential.VOLT),
#     "grid_freq": ("Grid Frequency", UnitOfFrequency.HERTZ),
#     "ac_output_voltage": ("AC Output Voltage", UnitOfElectricPotential.VOLT),
#     "ac_output_freq": ("AC Output Frequency", UnitOfFrequency.HERTZ),
#     "ac_output_va": ("AC Output Apparent Power", UnitOfApparentPower.VOLT_AMPERE),
#     "ac_output_w": ("AC Output Active Power", UnitOfPower.WATT),
#     "ac_output_percent": ("AC Output Load %", "%"),
#     "bus_voltage": ("Bus Voltage", UnitOfElectricPotential.VOLT),
#     "battery_voltage": ("Battery Voltage", UnitOfElectricPotential.VOLT),
#     "battery_charge_current": ("Battery Charge Current", UnitOfElectricCurrent.AMPERE),
# }

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN]
    coordinator = data["coordinator"]
    user_queries = data[CONF_QUERIES]

    entities = []
   
    for q in user_queries:
        for metric in q.metrics():
            entities.append(HidInverterNumberSensor(coordinator, entry.entry_id, metric.name, metric))

    add(entities)


class _Base(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry_id : str, name: str, meta : metric.Metric):
        super().__init__(coordinator)

        self._meta = meta

        self._attr_unique_id = f"{entry_id}-{meta.uuid}"
        self._attr_name = name

        self._attr_device_class = meta.dc
        self._attr_native_unit_of_measurement = meta.uom
        self._attr_state_class = meta.sc

    @property
    def available(self) -> bool:
        d = self.coordinator.data or {}
        return d.get(self._meta.uuid) is not None


class HidInverterNumberSensor(_Base):
    def __init__(self, coordinator, entry_id : str, name: str, meta : metric.Metric):
        super().__init__(coordinator, entry_id, name, meta)

    @property
    def native_value(self):
        d = self.coordinator.data or {}        
        return d.get(self._meta.uuid)