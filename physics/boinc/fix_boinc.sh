#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BOINC_SERVICE_DIR="/etc/systemd/system/boinc-client.service.d"

echo "Applying BOINC fixes."

echo "Suppressing log spam."
# https://wiki.archlinux.org/title/BOINC#Log_spam
mkdir -p "${BOINC_SERVICE_DIR}"
cp "${SCRIPT_DIR}/wayland-syslog-spam.conf" "${BOINC_SERVICE_DIR}/wayland-syslog-spam.conf"

echo "BOINC fixes ready."
