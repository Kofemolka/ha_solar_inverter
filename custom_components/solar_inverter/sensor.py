from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, CONF_QUERIES
from .queries import metric


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN]
    coordinator = data["coordinator"]
    user_queries = data[CONF_QUERIES]

    entities = []
   
    for q in user_queries:
        for metric in q.metrics():
            sensor = None

            if metric.uuid == 'mode':
                sensor = HidInverterModeSensor(coordinator, entry.entry_id, metric.name, metric)
            else:
                sensor = HidInverterNumberSensor(coordinator, entry.entry_id, metric.name, metric)

            entities.append(sensor)

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
        return bool(self.coordinator.data)


class HidInverterNumberSensor(_Base):
    def __init__(self, coordinator, entry_id : str, name: str, meta : metric.Metric):
        super().__init__(coordinator, entry_id, name, meta)

    @property
    def native_value(self):
        d = self.coordinator.data or {}        
        return d.get(self._meta.uuid)
    

class HidInverterModeSensor(_Base):
    MODE_MAP = {
        'P': 'power on',
        'S': 'standby',
        'L': 'grid',
        'B': 'battery',
        'F': 'fault',
        'H': 'hybernate',
        '' : 'unknown'
    }

    MODE_OPTIONS = list(sorted(set(MODE_MAP.values())))

    _attr_options = MODE_OPTIONS

    def __init__(self, coordinator, entry_id : str, name: str, meta : metric.Metric):
        super().__init__(coordinator, entry_id, name, meta)

    @property
    def native_value(self) -> str | None:
        d = self.coordinator.data or {}
        raw = d.get(self._meta.uuid)
        if not raw:
            return None
        return HidInverterModeSensor.MODE_MAP.get(raw, "unknown")