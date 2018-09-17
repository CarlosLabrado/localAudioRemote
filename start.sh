#!/usr/bin/env bash

# Make sure i2c is loaded
modprobe i2c-dev

# Start the fuse driver
systemctl start epd-fuse.service

papirus-set 2.7

python3 /build/papirus/papirus-clock.py