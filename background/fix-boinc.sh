#!/usr/bin/env sh
set -eu

# Fix BOINC suspension on computer use
# This is also in agx_startup.py, so it may not be necessary here.
xhost si:localuser:boinc
