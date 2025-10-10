from __future__ import annotations

import logging
from typing import Dict, Tuple, Optional
from .devices import fake, hidraw
from .queries import QUERIES


_LOGGER = logging.getLogger(__name__)
    
def _strip_frame(resp: bytes) -> str:
    return resp[1:-3].decode()


class InverterHub:
    def __init__(self, hass, path: str, name: str, queries):
        self.hass = hass
        self.name = name
        
        if path == "fake":
            self._dev = fake.FakeDevice()
        else:
            self._dev = hidraw.HidrawInverter(path)
        
        self._queries = list(queries)
        self._last = {}

    async def async_init(self):
        await self._dev.open()

    async def async_poll_all(self) -> Dict[str, dict]:
        data: Dict[str, dict] = {}
        for q in self._queries:
            try:
                raw = await self._dev.query(q.upper())
                parsed = self._parse(q, raw)
                data[q] = parsed
            except Exception as e:
                _LOGGER.warning("Query %s failed: %s", q, e)
        
        self._last = data
        return data
    
    def _parse(self, q: str, raw: bytes) -> dict:
        body = _strip_frame(raw)
        if body == "NAK":
            return {"ok": False}
        
        parts = body.split()
        
        for query in QUERIES:
            res = query.parse(q, parts)
            if res:
                return res
            
        return {"raw": body, "ok": True}        
        
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