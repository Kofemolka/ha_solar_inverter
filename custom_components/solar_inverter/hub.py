from __future__ import annotations

import asyncio

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import EVENT_HOMEASSISTANT_STOP

import logging
from typing import Dict
from .devices import fake, hidraw
from .queries import QUERIES


_LOGGER = logging.getLogger(__name__)
    
def _strip_frame(resp: bytes) -> str:
    return resp[1:-3].decode() # remove leading '(' and trailing CRC+'\r'


class InverterHub:
    def __init__(self, hass, path: str, name: str, queries : list):
        self.hass = hass
        self.name = name
        
        if path == "fake":
            self._dev = fake.FakeDevice()
        else:
            self._dev = hidraw.HidrawInverter(path)
        
        self._queries = queries
        self._unsub_stop = None

    async def async_init(self):        
        self._unsub_stop = self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP,
            lambda evt: self.hass.async_create_task(self.async_close())
        )

    async def async_close(self):
        if self._unsub_stop:
            self._unsub_stop()
            self._unsub_stop = None

    async def async_poll_all(self) -> Dict[str, dict]:
        data: Dict[str, dict] = {}
        for query in self._queries:
            try:
                raw = await self._dev.query(query.cmd())
                parsed = self._parse(query, raw)
                data |= parsed
            except Exception as e:
                _LOGGER.warning("Query %s failed: %s", query.cmd(), e)
            await asyncio.sleep(0.1)

        return data
    
    def _parse(self, query, raw: bytes) -> dict:
        body = _strip_frame(raw)
        if body == "NAK":
            return {"ok": False}
        
        parts = body.split()
        
        return query.parse(parts)