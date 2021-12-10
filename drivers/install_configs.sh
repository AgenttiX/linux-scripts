#!/bin/bash -e

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

echo "Installing configs."

XORG_CONF_DIR="/etc/X11/xorg.conf.d/"
cp "./xorg.conf.d/"*.conf "${XORG_CONF_DIR}"
chmod 644 "${XORG_CONF_DIR}"/*.conf

cp "./50-refresh-rate.conf" "/etc/environment.d/"
chmod 644 "/etc/environment.d/50-refresh-rate.conf"

echo "Configs installed."
