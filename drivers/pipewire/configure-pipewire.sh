#!/usr/bin/env bash
set -eu

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PIPEWIRE_CONF_DIR="/usr/share/pipewire"

if [ ! -d "${PIPEWIRE_CONF_DIR}" ]; then
  echo "PipeWire configuration directory was not found at \"${PIPEWIRE_CONF_DIR}\"."
  exit 1
fi

sudo cp "${SCRIPT_DIR}/agx-custom.conf" "${PIPEWIRE_CONF_DIR}/agx-custom.conf"

systemctl --user restart pipewire.service pipewire-pulse.service
