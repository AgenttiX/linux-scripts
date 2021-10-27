#!/bin/sh -e
# This script is called automatically by the udev rules.
# The placeholders are replaced by install_wacom.sh when this script is copied to /usr/local/bin.

sudo -u USERNAME python3 "SCRIPT_DIR/wacom.py"
