#!/usr/bin/bash -e
# https://rpcs3.net/quickstart

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# sudo apt-get update
# sudo apt-get install wget
# wget --content-disposition https://rpcs3.net/latest-appimage
# chmod +x ./rpcs3*.AppImage
flatpak install flathub net.rpcs3.RPCS3 com.github.tchx84.Flatseal

# CONFIG_PATH="${HOME}/.config/rpcs3"
CONFIG_PATH="${HOME}/.var/app/net.rpcs3.RPCS3/config/rpcs3"
if ! [ -L "$CONFIG_PATH" ]; then
  mkdir -p "$(dirname "${CONFIG_PATH}")"
  if [ -d "$CONFIG_PATH" ]; then
    mv "${CONFIG_PATH}" "${CONFIG_PATH}-old"
  fi
  ln -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
fi
echo "Installation ready. Use Flatseal to allow RPCS3 access to the configuration directory:"
echo "${SCRIPT_DIR}"
