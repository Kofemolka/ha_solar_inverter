from __future__ import annotations
import asyncio
import os
import fcntl
import logging
from typing import Dict, Tuple, Optional


_LOGGER = logging.getLogger(__name__)


class HidrawInverter:
    def __init__(self, path: str):
        self._path = path
        self._fd: Optional[int] = None
        self._lock = asyncio.Lock()
        self._loop = asyncio.get_event_loop()


    def _open_blocking(self):
        if self._fd is not None:
            return
        
        fd = os.open(self._path, os.O_RDWR | os.O_NONBLOCK)
        # set close-on-exec
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
        self._fd = fd


    async def open(self):
        await self._loop.run_in_executor(None, self._open_blocking)
        _LOGGER.info("Opened hidraw device %s", self._path)


    def close(self):
        if self._fd is not None:
            os.close(self._fd)
        self._fd = None

    @staticmethod
    def _crc16_ibm(data: bytes) -> Tuple[int, int]:
        crc = 0xFFFF
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
            lo = crc & 0xFF
            hi = (crc >> 8) & 0xFF
        return lo, hi
    
    @classmethod
    def build_cmd(cls, ascii_cmd: str) -> bytes:
        b = ascii_cmd.encode("ascii")
        lo, hi = cls._crc16_ibm(b)
        return b + bytes([lo, hi, 0x0D])


    def _write_blocking(self, data: bytes):
        assert self._fd is not None
        os.write(self._fd, data)

    def _read_until_cr_blocking(self, timeout: float) -> bytes:
        assert self._fd is not None
        import select
        buf = bytearray()
        end = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = end - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise TimeoutError("Read timeout")
            r, _, _ = select.select([self._fd], [], [], remaining)
            if not r:
                continue
            chunk = os.read(self._fd, 256)
            if not chunk:
                continue
            buf.extend(chunk)
            if buf and buf[-1] == 0x0D: # '\r'
                return bytes(buf)
            
    async def query(self, ascii_cmd: str, timeout: float = 2.0) -> bytes:
        async with self._lock:
            if self._fd is None:
                await self.open()
            req = self.build_cmd(ascii_cmd)
            await self._loop.run_in_executor(None, self._write_blocking, req)
            _LOGGER.debug("TX %s", ascii_cmd)
            resp = await self._loop.run_in_executor(None, self._read_until_cr_blocking, timeout)
            _LOGGER.debug("RX %r", resp)
            return resp
    
def _strip_frame(resp: bytes) -> str:
    # Responses like b"(230.0 50.0 ...)\r" or b"NAK\r"
    s = resp.decode("ascii", errors="ignore").strip()
    if s.startswith("(") and s.endswith("\r"):
        s = s[:-1]
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1]
    if s.endswith("\r"):
        s = s[:-1]
    return s


class InverterHub:
    def __init__(self, hass, path: str, name: str, queries):
        self.hass = hass
        self.name = name
        self._dev = HidrawInverter(path)
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
        if q == "qpigs":
            # General status (subset; indexes vary by model). We'll map safe basics.
            # Example (PIP-5048): (GridV GridF OutV OutF OutVA OutW OutPerc BusV BatV BatChgI ...)
            def f(i):
                try:
                    return float(parts[i])
                except Exception:
                    return None
                
            return {
                "grid_voltage": f(0),
                "grid_freq": f(1),
                "ac_output_voltage": f(2),
                "ac_output_freq": f(3),
                "ac_output_va": f(4),
                "ac_output_w": f(5),
                "ac_output_percent": f(6),
                "bus_voltage": f(7),
                "battery_voltage": f(8),
                "battery_charge_current": f(9),
                "raw": body,
                "ok": True,
            }
        
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