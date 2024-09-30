#!/bin/bash -eu

# This script is for reinstalling ROCm on Ubuntu after a broken update.
# Based on the official installation instructions.
# https://rocm.docs.amd.com/projects/install-on-linux/en/latest/index.html

# As of 2024-07-29, Ubuntu 24.04 is not yet officially supported.
# https://github.com/ROCm/ROCm/issues/2939
# https://askubuntu.com/questions/1517236/rocm-not-working-on-ubuntu-24-04-desktop

# Note that if you have "nomodeset" enabled:
# "WARNING: nomodeset detected in kernel parameters, amdgpu requires KMS"

ROCM_VERSION="6.1.2"
ROCM_VERSION2="6.1.60102-1"

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# echo "Which version of ROCm would you like to install? (Empty for latest.)"
# echo "Please have a look at https://repo.radeon.com/rocm/apt/ for the available versions."
# read -r ROCM_VERSION
# if [ -z "${ROCM_VERSION}" ]; then
#   echo "Using default version."
#   ROCM_VERSION="debian"
# else
#   echo "Using version: ${ROCM_VERSION}"
# fi

# echo "Which release channel would you like to use? (\"ubuntu\" for >= 4.20, \"xenial\" for older.)"
# read -r RELEASE_CHANNEL
# echo "Using release channel: ${RELEASE_CHANNEL}"

echo "Removing old ROCm installations."
# Removing "*amgdpu*" would cause the dependency tree of some higher-level packages to break,
# and the command below seems to be sufficient to fix the bugs such as CPU-only desktop rendering.
if command -v amdgpu-install >/dev/null 2>&1; then
  sudo amdgpu-install --uninstall --rocmrelease=all
fi
set +e
sudo apt purge --ignore-missing  amdgpu-install "rocm-*" "rock-*" rocminfo
set -e
sudo apt autoremove

sudo apt-get update
sudo apt-get dist-upgrade
# Prerequisites
# https://rocm.docs.amd.com/projects/install-on-linux/en/latest/how-to/prerequisites.html
# Clinfo is specified here to ensure that the debug info printing below works.
sudo apt-get install clinfo "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)" wget
# sudo apt-get install gnupg2 libnuma-dev

echo "Setting permissions"
sudo usermod -a -G render,video "${LOGNAME}"

# Installation using package manager
# wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
# echo "deb [arch=amd64] https://repo.radeon.com/rocm/apt/${ROCM_VERSION}/ ${RELEASE_CHANNEL} main" | sudo tee /etc/apt/sources.list.d/rocm.list

# Installation using amdgpu-install
FILENAME="amdgpu-install_${ROCM_VERSION2}_all.deb"
wget "https://repo.radeon.com/amdgpu-install/${ROCM_VERSION}/ubuntu/jammy/${FILENAME}" -O "${SCRIPT_DIR}/${FILENAME}"
sudo apt-get install "${SCRIPT_DIR}/${FILENAME}"

sudo apt-get update
sudo amdgpu-install --usecase=graphics,rocm
sudo apt-get install nvtop rocminfo rocm-smi

# The OpenCL packages should be included in the base rocm installation but are included here just in case.
# sudo apt-get install rocm-dev rocm-opencl-dev rocminfo


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
