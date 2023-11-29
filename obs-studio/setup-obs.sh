#!/usr/bin/env bash
set -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_PATH="${HOME}/.config/obs-studio"
CONFIG_PATH_FLATPAK="${HOME}/.var/app/com.obsproject.Studio/config/obs-studio"

sudo add-apt-repository ppa:obsproject/obs-studio

# https://github.com/obsproject/obs-studio/wiki/install-instructions#prerequisites-for-all-versions
sudo apt-get update
sudo apt-get install ffmpeg obs-studio v4l2loopback-dkms

# flatpak install flathub com.obsproject.Studio

if [ -d "${CONFIG_PATH}" ] && [ ! -L "${CONFIG_PATH}" ]; then
  echo "Backing up old OBS config directory."
  mv "${CONFIG_PATH}" "${CONFIG_PATH}-old"
fi
if [ -d "${CONFIG_PATH_FLATPAK}" ] && [ ! -L "${CONFIG_PATH_FLATPAK}" ]; then
  echo "Backing up old OBS flatpak config directory."
  mv "${CONFIG_PATH_FLATPAK}" "${CONFIG_PATH_FLATPAK}-old"
fi

echo "Creating symlinks."
ln -f -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
ln -f -s "${SCRIPT_DIR}" "${CONFIG_PATH_FLATPAK}"
echo "Configuration ready."
