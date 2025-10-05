#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

# CUDA
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu
CUDA_KEYRING="cuda-keyring_1.1-1_all.deb"
wget "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/${CUDA_KEYRING}" -O "${CUDA_KEYRING}"
dpkg -i "${CUDA_KEYRING}"

# Nvidia Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
