from __future__ import annotations

import logging
from typing import Dict, Tuple, Optional
from .devices import fake, hidraw
from .queries import QUERIES


_LOGGER = logging.getLogger(__name__)
    
def _strip_frame(resp: bytes) -> str:
    return resp[1:-3].decode()


class InverterHub:
    def __init__(self, hass, path: str, name: str, queries : list):
        self.hass = hass
        self.name = name
        
        if path == "fake":
            self._dev = fake.FakeDevice()
        else:
            self._dev = hidraw.HidrawInverter(path)
        
        self._queries = queries
        self._last = {}

    async def async_init(self):
        await self._dev.open()

    async def async_poll_all(self) -> Dict[str, dict]:
        data: Dict[str, dict] = {}
        for query in self._queries:
            try:
                raw = await self._dev.query(query.cmd())
                parsed = self._parse(query, raw)
                data |= parsed
            except Exception as e:
                _LOGGER.warning("Query %s failed: %s", query.cmd(), e)

        return data
    
    def _parse(self, query, raw: bytes) -> dict:
        body = _strip_frame(raw)
        if body == "NAK":
            return {"ok": False}
        
        parts = body.split()
        
        return query.parse(parts)       
        
        if q == "qpiri":
            # Rated info (subset)
            def f(i):
                try:
                    return float(parts[i])
                except Exception:
                    return None
                
            return {
                "ac_input_rating_voltage": f(0),
                "ac_input_rating_freq": f(1),
                "ac_output_rating_voltage": f(2),
                "ac_output_rating_freq": f(3),
                "ac_output_rating_current": f(4),
                "ac_output_rating_apparent_power": f(5),
                "ac_output_rating_active_power": f(6),
                "battery_rating_voltage": f(7),
                "battery_recharge_voltage": f(8),
                "battery_redischarge_voltage": f(9),
                "raw": body,
                "ok": True,
            }
        
        if q == "qpiws":
            # Warning status bits: provide as raw string + echo list
            return {
                "warnings": parts,
                "raw": body,
                "ok": True,
            }
        
        return {"raw": body, "ok": True}