import os
import fcntl
import select
import asyncio

import logging

_LOGGER = logging.getLogger(__name__)


class HidrawInverter():
    _TA = [
        0x0000,0x1021,0x2042,0x3063,0x4084,0x50a5,0x60c6,0x70e7,
        0x8108,0x9129,0xa14a,0xb16b,0xc18c,0xd1ad,0xe1ce,0xf1ef
    ]

    _FORBIDDEN_BYTES = [ 0x0A, 0x0D, 0x28 ]

    def __init__(self, device_path):
        self._device_path = device_path

    @staticmethod
    def _open(path):
        fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
        # CLOEXEC
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)

        return fd
   
    @staticmethod
    def _close(fd):
        os.close(fd)

    async def query(self, cmd: str) -> bytes:
        fd = 0

        try:
            fd = self._open(self._device_path)
        
            encoded = HidrawInverter._encode(cmd)

            os.write(fd, encoded)

            resp = await self._read(fd)

            return resp

        except Exception as e:
            _LOGGER.error(f"Error reading from the {self._device_path}: {e}")
        finally:
            self._close(fd)

        return bytes()
    
    @staticmethod
    async def _read(fd, overall=2.0, interbyte=0.5, chunk=128, max_bytes=4096) -> bytes:
        rxbuf = bytearray()
        deadline = asyncio.get_running_loop().time() + overall
        while True:
            # already have a frame?
            try:
                i = rxbuf.index(0x0D)  # '\r'
                frame = bytes(rxbuf[:i+1])
                del rxbuf[:i+1]
                return frame
            except ValueError:
                pass

            remain = deadline - asyncio.get_running_loop().time()
            if remain <= 0:
                raise asyncio.TimeoutError("overall timeout")

            timeout = min(interbyte, remain)

            # wait for readability without blocking the event loop
            r, _, _ = await asyncio.get_running_loop().run_in_executor(
                None, select.select, [fd], [], [], timeout
            )
            if not r:
                raise asyncio.TimeoutError("inter-byte timeout")

            # non-blocking read (device may return >chunk)
            data = os.read(fd, chunk)
            if data:
                rxbuf.extend(data)
                if len(rxbuf) > max_bytes:
                    raise ValueError("max_bytes exceeded")
    
    @staticmethod
    def _encode(req : str) -> bytearray:
        payload = bytearray(req.encode('utf-8'))
        crc = HidrawInverter._calc_crc(payload)
        payload.append((crc >> 8) & 0xFF)
        payload.append(crc & 0xFF)
        payload.append(0x0D)

        return payload

    @staticmethod
    def _calc_crc(data):
        crc = 0

        for i in range(len(data)):
            da=((crc>>8) & 0xFF) >> 4
            crc = (crc << 4) & 0xFFFF
            index = da ^ (data[i] >> 4)
            mask = HidrawInverter._TA[index]
            crc = crc ^ mask

            da=((crc>>8) & 0xFF) >> 4
            crc = (crc << 4) & 0xFFFF
            index = da ^ (data[i] & 0x0F)
            mask = HidrawInverter._TA[index]
            crc = crc ^ mask

        if (crc & 0xFF) in HidrawInverter._FORBIDDEN_BYTES:
            crc = crc + 0x01
        if (crc >> 8) in HidrawInverter._FORBIDDEN_BYTES:
            crc = crc + 0x100

        return crc