#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

mkdir -p /etc/pipewire/pipewire.conf.d
cp "${SCRIPT_DIR}/crackling.conf" "/etc/pipewire/pipewire.conf.d/crackling.conf"

systemctl --user restart pipewire.service pipewire-pulse.service
