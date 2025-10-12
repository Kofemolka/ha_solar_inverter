from __future__ import annotations
import logging
from datetime import timedelta


import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform


from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_DEVICE,
    CONF_SCAN_INTERVAL,
    CONF_QUERIES,
    DEFAULT_SCAN_INTERVAL,
    SUPPORTED_QUERIES,
)
from .hub import InverterHub
from .queries import get_user_queries


_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICE): cv.string,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.positive_int,
                vol.Optional(
                    CONF_QUERIES, default=list(sorted(SUPPORTED_QUERIES))
                ): vol.All(cv.ensure_list, [vol.In(SUPPORTED_QUERIES)]),
                vol.Optional(CONF_NAME, default="Inverter"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Import YAML into a ConfigEntry (one entry only)."""
    conf = config.get(DOMAIN)
    if not conf:
        return True
    # Create/update config entry from YAML
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=conf,
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    device: str = entry.data[CONF_DEVICE]
    scan_seconds = entry.data[CONF_SCAN_INTERVAL]
    user_queries = entry.data[CONF_QUERIES]
    name = entry.data[CONF_NAME]

    device_id = f"{name}:{device}"
    devreg = dr.async_get(hass)
    devreg.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, device_id)},
        manufacturer="n/a",
        model="n/a",
        name=device_id,
        sw_version="n/a",
    )

    selected_queries = get_user_queries(user_queries)
  
    hub = InverterHub(hass, device, name=name, queries=selected_queries)
    await hub.async_init()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_coordinator",
        update_method=hub.async_poll_all,
        update_interval=timedelta(seconds=scan_seconds),
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = {
        "hub": hub,
        "coordinator": coordinator,
        "name": name,
        "queries": selected_queries,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data:
        hub: InverterHub = data["hub"]
        if hub:
            await hub.async_close()
    return True