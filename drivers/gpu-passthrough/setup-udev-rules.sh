#!/usr/bin/env bash

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Configuring udev rules."
cp "${SCRIPT_DIR}/40-passthrough.rules" "/etc/udev/rules.d/40-passthrough.rules"
echo "Udev rules configured."

echo "Currently set up udev rules at \"/etc/udev/rules.d\":"
ls "/etc/udev/rules.d"

echo "Status of udev rules:"
udevadm verify
