#!/usr/bin/bash -e
# https://github.com/stenzek/duckstation

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

sudo apt-get update
sudo apt-get install wget

wget "https://github.com/stenzek/duckstation/releases/download/latest/duckstation-qt-x64.AppImage" -O "./duckstation-qt-x64.AppImage"
chmod +x "./duckstation-qt-x64.AppImage"

CONFIG_PATH="${HOME}/.local/share/duckstation"
if ! [ -L "$CONFIG_PATH" ]; then
  mkdir -p "$(dirname "${CONFIG_PATH}")"
  if [ -d "$CONFIG_PATH" ]; then
    rm -r "${CONFIG_PATH}"
  fi
  ln -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
fi
