#!/usr/bin/env python3
import os, fcntl, socket, select, argparse

def open_hid(path: str) -> int:
    fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
    return fd

def relay_once(hid_fd: int, conn: socket.socket):
    rlist, _, _ = select.select([hid_fd, conn], [], [], 1.0)
    if hid_fd in rlist:
        try:
            data = os.read(hid_fd, 4096)
            if data:
                conn.sendall(data)
        except BlockingIOError:
            pass
    if conn in rlist:
        data = conn.recv(4096)
        if data:
            os.write(hid_fd, data)
        else:
            raise ConnectionError("client closed")

def serve(dev: str, host: str, port: int):
    hid_fd = open_hid(dev)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        print(f"Bridge ready on {host}:{port} -> {dev}")
        while True:
            conn, addr = s.accept()
            print(f"Client {addr} connected")
            with conn:
                try:
                    while True:
                        relay_once(hid_fd, conn)
                except Exception as e:
                    print(f"Client {addr} disconnected: {e}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", default="/dev/hidraw0")
    ap.add_argument("--host", default="0.0.0.0")   # bind locally; tunnel from dev box
    ap.add_argument("--port", type=int, default=9009)
    args = ap.parse_args()
    serve(args.dev, args.host, args.port)

# How To
# 1. In the terminal on the HA instance, run the tcp_bridge:
# > tcp_bridge.py --dev /dev/hidraw0 --host 0.0.0.0 --port 9009
# 
# In your devcontainer, create pipe:
# > test/pipe.bash
# Or pty_bridge: 
#
# In your config, point to a pipe device:
# solar_inverter:
#   device: /tmp/inverter