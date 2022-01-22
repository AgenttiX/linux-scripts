#!/usr/bin/bash -e
# https://rpcs3.net/quickstart

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

sudo apt-get update
sudo apt-get install wget
wget --content-disposition https://rpcs3.net/latest-appimage
chmod +x ./rpcs3*.AppImage

CONFIG_PATH="${HOME}/.config/rpcs3"
if ! [ -L "$CONFIG_PATH" ]; then
  mkdir -p "$(dirname "${CONFIG_PATH}")"
  if [ -d "$CONFIG_PATH" ]; then
    rm -r "${CONFIG_PATH}"
  fi
  ln -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
fi
