#!/bin/bash -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DIR="${SCRIPT_DIR}/logs/report"

if [ -z "${DIR}" ]; then
  echo "Could not configure directory variable: ${DIR}"
  exit 1
fi

# Install dependencies
sudo apt-get update
sudo apt-get install clinfo dmidecode lshw lsscsi p7zip vainfo vdpauinfo

mkdir -p "${DIR}"
# Remove old results
if [ "$(ls -A $DIR)" ]; then
  rm -r "${DIR:?}"/*
fi
mkdir -p "${DIR}/hdparm" "${DIR}/smartctl"

# Basic info
echo -n "Hostname: "
hostname |& tee -a "${DIR}/basic.txt"
echo -n "Uname: "
uname -a |& tee -a "${DIR}/basic.txt"
echo "HDDs" |& tee -a "${DIR}/basic.txt"
smartctl --scan |& tee -a "${DIR}/basic.txt"

# Non-root info
lsblk -a &> "${DIR}/lsblk.txt"
lscpu &> "${DIR}/lscpu.txt"

lspci &> "${DIR}/lspci.txt"
lsscsi &> "${DIR}/lsscsi.txt"
lsusb &> "${DIR}/lsusb.txt"

vainfo &> "${DIR}/vainfo.txt"
vdpauinfo &> "${DIR}/vdpauinfo.txt"

xinput list &> "${DIR}/xinput.txt"
xrandr &> "${DIR}/xrandr.txt"

# Root info
sudo dmidecode &> "${DIR}/dmidecode.txt"
sudo lshw -html > "${DIR}/lshw.html"

# Storage devices
mapfile -t SMARTCTL_SCAN < <(smartctl --scan)
for LINE in "${SMARTCTL_SCAN[@]}"; do
  IFS=', ' read -r -a ARR <<< "${LINE}"
  DISK="${ARR[0]}"
  DISK_NAME="$(basename "${DISK}")"
  sudo hdparm -I "${DISK}" &> "${DIR}/hdparm/${DISK_NAME}"
  sudo smartctl --all "${DISK}" &> "${DIR}/smartctl/${DISK_NAME}"
done

# GPU info
if command -v clinfo &> /dev/null; then
  clinfo &> "${DIR}/clinfo.txt"
else
  echo "nvidia-smi was not found. This system probably doesn't have Nvidia GPUs installed."
fi

if command -v nvidia-smi &> /dev/null; then
  nvidia-smi &> "${DIR}/nvidia-smi.txt"
else
  echo "nvidia-smi was not found. This system probably doesn't have Nvidia GPUs installed."
fi

if command -v rocminfo &> /dev/null; then
  rocminfo &> "${DIR}/rocminfo.txt"
else
  echo "rocminfo was not yet found."
fi

if command -v rocm-smi &> /dev/null; then
  rocm-smi &> "${DIR}/rocm-smi.txt"
else
  echo "rocm-smi was not yet found."
fi

# Packaging
7zr a -mx=9 "${DIR}_$(date '+%Y-%m-%d_%H-%M-%S').7z" "${DIR}"
echo "The report is ready."
