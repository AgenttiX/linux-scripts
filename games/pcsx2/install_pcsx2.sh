#!/usr/bin/bash -e
# https://github.com/PCSX2/pcsx2/wiki/Installing-on-Linux
# https://launchpad.net/%7Epcsx2-team/+archive/ubuntu/pcsx2-daily

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# The official repository does not have a proper Release file and therefore does not work properly.
# At the moment the official builds are 32-bit only, and therefore adding the i386 architecture is necessary.
# sudo dpkg --add-architecture i386
# sudo add-apt-repository ppa:gregory-hainaut/pcsx2.official.ppa

# The daily repository has 64-bit builds.
# However, the package "pcsx2" may still be 32-bit only.
# sudo add-apt-repository ppa:pcsx2-team/pcsx2-daily

# sudo apt-get update
# sudo apt-get install pcsx2
flatpak install flathub net.pcsx2.PCSX2

# CONFIG_PATH="${HOME}/.config/PCSX2"
CONFIG_PATH="${HOME}/.var/app/net.pcsx2.PCSX2/config/PCSX2"
if ! [ -L "$CONFIG_PATH" ]; then
  mkdir -p "$(dirname "${CONFIG_PATH}")"
  if [ -d "$CONFIG_PATH" ]; then
    mv "${CONFIG_PATH}" "${CONFIG_PATH}-old"
  fi
  ln -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
fi
