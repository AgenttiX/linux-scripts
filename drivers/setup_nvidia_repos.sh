#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

VERSION="2604"
for i in "$@"; do
  case $i in
    -v=*|--version=*)
      VERSION="${i#*=}"
      shift # past argument-value
      ;;
    -*|--*)
      echo "Unknown option $i"
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# CUDA
# https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu
CUDA_KEYRING="cuda-keyring_1.1-1_all.deb"
CUDA_KEYRING_PATH="${SCRIPT_DIR}/${CUDA_KEYRING}"
wget "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu${VERSION}/x86_64/${CUDA_KEYRING}" -O "${CUDA_KEYRING_PATH}"
apt install curl "${CUDA_KEYRING_PATH}"

# Nvidia Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor --yes -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

apt update
