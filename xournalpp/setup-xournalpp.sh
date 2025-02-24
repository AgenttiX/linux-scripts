#!/usr/bin/env bash
set -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_DIR="${HOME}/.config/xournalpp"
CONFIG_DIR2="${HOME}/.var/app/com.github.xournalpp.xournalpp/config/xournalpp"

flatpak install flathub com.github.xournalpp.xournalpp

# Backup old configs
if [ -e "${CONFIG_DIR}" ] && [ ! -L "${CONFIG_DIR}" ]; then
  echo "Backing up old configuration."
  mv "${CONFIG_DIR}" "${CONFIG_DIR}-old"
fi
if [ -e "${CONFIG_DIR2}" ] && [ ! -L "${CONFIG_DIR2}" ]; then
  echo "Backing up old Flatpak configuration."
  mv "${CONFIG_DIR2}" "${CONFIG_DIR2}-old"
fi

echo "Creating symlinks."
ln -f -s "${SCRIPT_DIR}" "${CONFIG_DIR}"
ln -f -s "${SCRIPT_DIR}" "${CONFIG_DIR2}"
