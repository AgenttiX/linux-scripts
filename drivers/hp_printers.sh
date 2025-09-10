#!/usr/bin/env sh
set -eu

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

sudo apt update
sudo apt install hplip hplip-gui ipp-usb sane-airscan xsane

scanimage --list-devices

if [ -f "/etc/papersize" ]; then
  echo "Default paper size in your system:"
  cat /etc/papersize
fi
