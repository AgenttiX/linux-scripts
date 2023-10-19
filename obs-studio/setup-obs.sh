#!/usr/bin/env bash
set -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_PATH="${HOME}/.var/app/com.obsproject.Studio/config/obs-studio"

flatpak install flathub com.obsproject.Studio

if [ -d "${CONFIG_PATH}" ] && [ ! -L "${CONFIG_PATH}" ]; then
  echo "Backing up old config directory."
  mv "${CONFIG_PATH}" "${CONFIG_PATH}-old"
fi
# Non-flatpak config directory:
# "${HOME}/.config/obs-studio"

echo "Creating symlink."
ln -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
echo "Configuration ready."
