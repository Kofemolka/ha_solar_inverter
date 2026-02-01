from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_QUERIES

from .entity import BaseEntity


class BaseSelect(BaseEntity, SelectEntity):
    def __init__(self, coordinator, hub, entry_id : str, name: str, meta):
        super().__init__(coordinator, entry_id, name, meta)

        self._hub = hub


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN]
    coordinator = data["coordinator"]
    hub = data["hub"]
    user_queries = data[CONF_QUERIES]

    entities = []
   
    for q in user_queries:
        for metric in q.metrics():
            selector = None

            if metric.uuid == 'output_source_priority':
                selector = HidInverterSourcePrioritySensor(coordinator, hub, entry.entry_id, metric.name, metric)

            if selector:
                entities.append(selector)

    add(entities)


class HidInverterSourcePrioritySensor(BaseSelect):
    SRC_MAP = {
        0: "Utility first",
        1: "Solar first",
        2: "Solar, Battery, Utility",
    }
    SRC_INV = {v: k for k, v in SRC_MAP.items()}

    _attr_options = list(SRC_MAP.values())

    @property
    def current_option(self) -> str | None:
        d = self.coordinator.data or {}
        raw = d.get(self._meta.uuid)
        if raw is None:
            return None
        return self.SRC_MAP.get(raw)

    async def async_select_option(self, option: str) -> None:
        raw = self.SRC_INV[option]

        if await self._hub.set_output_source_priority(raw):
            await self.coordinator.async_request_refresh()