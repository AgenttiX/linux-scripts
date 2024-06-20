#!/usr/bin/env bash
set -eu

# Based on
# https://askubuntu.com/a/1124256/

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -d "${HOME}/Git" ]; then
  GIT_DIR="${HOME}/Git"
else
  GIT_DIR=SCRIPT_DIR
fi

FIRMWARE_REPO_DIR="${GIT_DIR}/linux-firmware"
if [ -d "${FIRMWARE_REPO_DIR}" ]; then
  cd "${FIRMWARE_REPO_DIR}"
  git pull
else
  cd "${GIT_DIR}"
  git clone "git://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git"
fi

BACKUP_DIR="${SCRIPT_DIR}/backup/amdgpu_$(date +%s)"
FIRMWARE_DIR="/lib/firmware/amdgpu"
mkdir -p "${BACKUP_DIR}"
cp "${FIRMWARE_DIR}"/* "${BACKUP_DIR}"
sudo cp "${FIRMWARE_REPO_DIR}/amdgpu"/* "${FIRMWARE_DIR}"
