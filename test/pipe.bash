#!/usr/bin/env bash

set -e

while true; do
  echo "[socat] starting…"
  socat -d -d -v \
    pty,raw,echo=0,link=/tmp/inverter,wait-slave \
    tcp:192.168.0.250:9009,keepalive,forever,interval=2
  echo "[socat] exited, restarting in 1s…"
  sleep 1
done