#!/usr/bin/env sh
set -eu

# Fix BOINC suspension on computer use
xhost si:localuser:boinc
