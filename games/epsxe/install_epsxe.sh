#!/usr/bin/bash -e
# The direct installation does not work on new Ubuntu versions due to library conflicts.
# The preferred way to install is from a snap as below.

if [ "${EUID}" -eq 0 ]; then
   echo "This script should be run as root."
   exit 1
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# sudo apt-get install libsdl-ttf2.0-0

# wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0.0_1.0.2n-1ubuntu5.7_amd64.deb
# wget http://archive.ubuntu.com/ubuntu/pool/universe/c/curl3/libcurl3_7.58.0-2ubuntu2_amd64.deb
# sudo dpkg -i sudo libssl1.0.0_1.0.2n-1ubuntu5.7_amd64.deb

# libcurl3 cannot be installed with dpkg, as it conflicts with the existing libcurl4
# sudo dpkg -i libcurl3_7.58.0-2ubuntu2_amd64.deb
# dpkg -x libcurl3_7.58.0-2ubuntu2_amd64.deb ./libcurl
# mv

#####################
# Snap installation #
#####################

sudo snap install --candidate epsxe

CONFIG_PATH="/home/${USER}/snap/epsxe/1/.epsxe"
if ! [ -L "$CONFIG_PATH" ]; then
  mkdir -p "$(dirname "${CONFIG_PATH}")"
  if [ -d "$CONFIG_PATH" ]; then
    rm -r "${CONFIG_PATH}"
  fi
  ln -s "${SCRIPT_DIR}" "${CONFIG_PATH}"
fi
