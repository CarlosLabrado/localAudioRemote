#!/usr/bin/env bash

# Make sure i2c is loaded
modprobe i2c-dev

papirus-set 2.7

python /build/papirus/main.py