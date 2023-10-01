#!/usr/bin/env bash
set -e

# Based on:
# https://askubuntu.com/a/1009096/

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_SOURCE="${SCRIPT_DIR}/50unattended-upgrades"
CONFIG_TARGET="/etc/apt/apt.conf.d/50unattended-upgrades"
CONFIG_FILE_BACKUP="${SCRIPT_DIR}/50unattended-upgrades.bak"
SCRIPT_SOURCE="${SCRIPT_DIR}/reboot_if_needed.sh"
SCRIPT_TARGET="/usr/local/bin/reboot_if_needed.sh"

if [ -f "${CONFIG_TARGET}" ]; then
  if [ ! -f "${CONFIG_FILE_BACKUP}}" ]; then
    echo "Backing up old configuration to .bak"
    cp "${CONFIG_TARGET}" "${CONFIG_FILE_BACKUP}"
  else
    echo "Backup already exists."
  fi
else
  echo "No previous config file was found. No need to backup."
fi

echo "Installing config."
cp "${CONFIG_SOURCE}" "${CONFIG_TARGET}"
chown root:root "${CONFIG_TARGET}"
chmod 644 "${CONFIG_TARGET}"

echo "Installing script."
cp "${SCRIPT_SOURCE}" "${SCRIPT_TARGET}"
chown root:root "${SCRIPT_TARGET}"
chmod 755 "${SCRIPT_TARGET}"

echo "Ready. Please add something like this to \"sudo crontab -e\":"
echo "0 03 * * 7 ${SCRIPT_TARGET} >> /var/log/reboot_history.log"
