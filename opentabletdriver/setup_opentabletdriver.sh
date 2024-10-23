#!/usr/bin/env bash
set -eu

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_PATH="${HOME}/.config/OpenTabletDriver"
FILENAME="OpenTabletDriver.deb"

# Required for the dotnet-runtime-6.0 dependency
sudo add-apt-repository ppa:dotnet/backports
wget "https://github.com/OpenTabletDriver/OpenTabletDriver/releases/latest/download/${FILENAME}" -O "${SCRIPT_DIR}/${FILENAME}"

# You may have to install dotnet-runtime-6.0 as well
sudo apt-get install "${SCRIPT_DIR}/${FILENAME}"

if [ -d "${CONFIG_PATH}" ] && [ ! -L "${CONFIG_PATH}" ]; then
  echo "Backing up old config directory."
  mv "${CONFIG_PATH}" "${CONFIG_PATH}-old"
fi

echo "Creating symlink."
ln -f -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
echo "Configuration ready."
