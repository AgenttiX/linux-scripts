#!/usr/bin/bash -e
# https://github.com/stenzek/duckstation

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

sudo apt update
sudo apt install wget

FILENAME="DuckStation-x64.AppImage"
wget "https://github.com/stenzek/duckstation/releases/download/latest/${FILENAME}" -O "${SCRIPT_DIR}/${FILENAME}"
chmod +x "${SCRIPT_DIR}/${FILENAME}"

CONFIG_PATH="${HOME}/.local/share/duckstation"
if ! [ -L "$CONFIG_PATH" ]; then
  mkdir -p "$(dirname "${CONFIG_PATH}")"
  if [ -d "$CONFIG_PATH" ]; then
    mv "${CONFIG_PATH}" "${HOME}/DuckStation-old-config-backup"
  fi
  ln -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
fi
