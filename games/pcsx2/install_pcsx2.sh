#!/usr/bin/bash -e
# https://github.com/PCSX2/pcsx2/wiki/Installing-on-Linux
# https://launchpad.net/%7Epcsx2-team/+archive/ubuntu/pcsx2-daily

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Previously the official repository did not have a proper Release file and therefore did not work properly.
# sudo dpkg --add-architecture i386
# sudo add-apt-repository ppa:gregory-hainaut/pcsx2.official.ppa

# As of 2025, this PPA repository has old builds.
# sudo add-apt-repository ppa:pcsx2-team/pcsx2-daily

# sudo apt-get update
# sudo apt-get install pcsx2
flatpak install flathub net.pcsx2.PCSX2
flatpak --user override --filesystem=home net.pcsx2.PCSX2

CONFIG_PATH="${HOME}/.config/PCSX2"
CONFIG_PATH2="${HOME}/.var/app/net.pcsx2.PCSX2/config/PCSX2"
SYNCTHING_PATH="${HOME}/Syncthing/MikanHolvi"
MEMCARD_SYNC_PATH="${SYNCTHING_PATH}/PS2"
MEMCARD_PATH="${SCRIPT_DIR}/memcards"

if ! [ -L "${CONFIG_PATH}" ]; then
  mkdir -p "$(dirname "${CONFIG_PATH}")"
  if [ -d "${CONFIG_PATH}" ]; then
    mv "${CONFIG_PATH}" "${CONFIG_PATH}-old"
  fi
  ln -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
fi
if ! [ -L "${CONFIG_PATH2}" ]; then
  mkdir -p "$(dirname "${CONFIG_PATH2}")"
  if [ -d "${CONFIG_PATH2}" ]; then
    mv "${CONFIG_PATH2}" "${CONFIG_PATH2}-old"
  fi
  ln -s "${SCRIPT_DIR}" "${CONFIG_PATH2}"
fi

if [ -d "${SYNCTHING_PATH}" ]; then
  echo "Syncthing folder found. Configuring memory card syncing."
  if ! [ -L "${MEMCARD_PATH}" ]; then
    mkdir -p "${MEMCARD_SYNC_PATH}"
    mkdir -p "$(dirname "${MEMCARD_PATH}")"
    if [ -d "${MEMCARD_PATH}" ]; then
      mv "${MEMCARD_PATH}" "${MEMCARD_PATH}-old"
    fi
    ln -s "${MEMCARD_SYNC_PATH}" "${MEMCARD_PATH}"
  fi
else
  echo "Syncthing folder was not found. Skipping memory card sync configuration."
fi
