#!/usr/bin/env python3
import os, fcntl, json, time, argparse, select, sys

_TA = [
    0x0000,0x1021,0x2042,0x3063,0x4084,0x50a5,0x60c6,0x70e7,
    0x8108,0x9129,0xa14a,0xb16b,0xc18c,0xd1ad,0xe1ce,0xf1ef
]

_FORBIDDEN_BYTES = [ 0x0A, 0x0D, 0x28 ]

def calc_crc(data):
    crc = 0

    for i in range(len(data)):
        da=((crc>>8) & 0xFF) >> 4
        crc = (crc << 4) & 0xFFFF
        index = da ^ (data[i] >> 4)
        mask = _TA[index]
        crc = crc ^ mask

        da=((crc>>8) & 0xFF) >> 4
        crc = (crc << 4) & 0xFFFF
        index = da ^ (data[i] & 0x0F)
        mask = _TA[index]
        crc = crc ^ mask

    if (crc & 0xFF) in _FORBIDDEN_BYTES:
        crc = crc + 0x01
    if (crc >> 8) in _FORBIDDEN_BYTES:
        crc = crc + 0x100

    return crc

def crc16_ibm(data: bytes):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def build_cmd(cmd: str) -> bytes:
    payload = bytearray(cmd.encode('utf-8'))
    crc = calc_crc(payload)
    payload.append((crc >> 8) & 0xFF)
    payload.append(crc & 0xFF)
    payload.append(0x0D)
    return payload


def read_until_cr(fd: int, timeout: float = 2.0) -> bytes:
    buf = bytearray()
    import select, time, os
    end = time.time() + timeout
    while True:
        # already have a full frame?
        try:
            i = buf.index(0x0D)  # b'\r'
            frame = bytes(buf[:i+1])
            del buf[:i+1]        # leave remainder in buf for next call
            return frame
        except ValueError:
            pass  # need more data

        remain = end - time.time()
        if remain <= 0:
            raise TimeoutError("timeout")

        r, _, _ = select.select([fd], [], [], remain)
        if not r:
            continue

        chunk = os.read(fd, 4096)
        if chunk:
            buf.extend(chunk)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", required=True)   # e.g. /dev/hidraw0
    ap.add_argument("--out", default="samples.json")
    ap.add_argument("--cmds", default="QPIGS,QPIRI,QPIWS")
    args = ap.parse_args()

    fd = os.open(args.device, os.O_RDWR | os.O_NONBLOCK)
    # close-on-exec
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)

    samples = []
    for name in [c.strip() for c in args.cmds.split(",") if c.strip()]:
        req = build_cmd(name)
        os.write(fd, req)
        t0 = time.time()
        try:
            resp = read_until_cr(fd, timeout=3.0)
        except Exception as e:
            print(f"{name}: read failed: {e}", file=sys.stderr)
            continue
        t1 = time.time()
        # Store both ascii-ish and hex
        samples.append({
            "cmd": name,
            "tx_hex": req.hex(),
            "rx_hex": resp.hex(),
            "rx_ascii": resp.decode("ascii", errors="ignore"),
            "t_start": t0,
            "t_end": t1,
        })
        time.sleep(0.4)

    os.close(fd)
    with open(args.out, "w") as f:
        json.dump(samples, f, indent=2)
    print(f"Saved {len(samples)} samples → {args.out}")

if __name__ == "__main__":
    main()