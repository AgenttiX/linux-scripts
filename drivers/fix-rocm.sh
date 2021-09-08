#!/bin/bash -e

# This script is for reinstalling ROCm on Ubuntu after a broken update.
# Based on the official installation instructions.
# https://rocmdocs.amd.com/en/latest/Installation_Guide/Installation-Guide.html

if [ "$EUID" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

echo "Which version of ROCm would you like to install? (Empty for latest.)"
echo "Please have a look at https://repo.radeon.com/rocm/apt/ for the available versions."
read -r ROCM_VERSION
if [ -z "${ROCM_VERSION}" ]; then
  echo "Using default version."
  ROCM_VERSION="debian"
else
  echo "Using version: ${ROCM_VERSION}"
fi

echo "Which release channel would you like to use? (\"ubuntu\" for >= 4.20, \"xenial\" for older.)"
read -r RELEASE_CHANNEL
echo "Using release channel: ${RELEASE_CHANNEL}"

echo "Removing old ROCm installation."
# Removing "*amgdpu*" would cause the dependency tree of some higher-level packages to break,
# and the command below seems to be sufficient to fix the bugs such as CPU-only desktop rendering.
sudo apt purge --ignore-missing  "rocm-*" "rock-*" rocminfo
sudo apt autoremove

sudo apt-get update
sudo apt-get dist-upgrade
# Clinfo is specified here to ensure that the debug info printing below works.
sudo apt install clinfo gnupg2 libnuma-dev wget

wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo "deb [arch=amd64] https://repo.radeon.com/rocm/apt/${ROCM_VERSION}/ ${RELEASE_CHANNEL} main" | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt-get update

# The OpenCL packages should be included in the base rocm installation but are included here just in case.
sudo apt-get install rocm-dev rocm-opencl-dev rocminfo

echo "Printing debug info. It may take a reboot for it to update."
clinfo

if command -v nvidia-smi &> /dev/null; then
  which nvidia-smi
  nvidia-smi
else
  echo "nvidia-smi was not found. This system probably doesn't have Nvidia GPUs installed."
fi

if command -v rocminfo &> /dev/null; then
  which rocminfo
  rocminfo
else
  echo "rocminfo was not yet found."
fi

if command -v rocm-smi &> /dev/null; then
  which rocm-smi
  rocm-smi
else
  echo "rocm-smi was not yet found."
fi

echo "Please reboot to ensure that the GPU is found properly."
