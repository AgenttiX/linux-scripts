#!/bin/bash -e

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

XORG_CONF_DIR="/etc/X11/xorg.conf.d/"
cp "./10-amd-primary-gpu.conf" "${XORG_CONF_DIR}"
cp "./20-hdr.conf" "${XORG_CONF_DIR}"
chmod 644 "${XORG_CONF_DIR}"/10-amd-primary-gpu.conf "${XORG_CONF_DIR}/20-hdr.conf"
