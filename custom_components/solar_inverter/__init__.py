from __future__ import annotations
import logging
from datetime import timedelta


import voluptuous as vol
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
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


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    device = conf[CONF_DEVICE]
    scan_seconds = conf[CONF_SCAN_INTERVAL]
    queries = conf[CONF_QUERIES]
    name = conf[CONF_NAME]

    hub = InverterHub(hass, device, name=name, queries=queries)
    await hub.async_init()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_coordinator",
        update_method=hub.async_poll_all,
        update_interval=timedelta(seconds=scan_seconds),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = {
        "hub": hub,
        "coordinator": coordinator,
        "name": name,
        "queries": queries,
    }

    for platform in PLATFORMS:
        hass.async_create_task(async_load_platform(hass, platform, DOMAIN, {}, config))

    return True