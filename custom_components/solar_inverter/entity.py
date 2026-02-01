from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .queries import metric


class BaseEntity(CoordinatorEntity):
    def __init__(self, coordinator, entry_id : str, name: str, meta : metric.Metric):
        super().__init__(coordinator)

        self._meta = meta
        self._attr_unique_id = f"{entry_id}-{meta.uuid}"
        self._attr_name = name

    @property
    def available(self) -> bool:
        return bool(self.coordinator.data)