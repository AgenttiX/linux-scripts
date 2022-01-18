#!/bin/bash -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export DIR="${SCRIPT_DIR}/report"

if [ -z "${DIR}" ]; then
  echo "Could not configure directory variable: ${DIR}"
  exit 1
fi

# Install dependencies
sudo apt-get update
sudo apt-get install clinfo dmidecode i2c-tools lshw lsscsi p7zip vainfo vdpauinfo
# Load kernel modules for decode-dimms
# https://superuser.com/a/1499521/
sudo modprobe at24
sudo modprobe ee1004
sudo modprobe eeprom
sudo modprobe i2c-i801
sudo modprobe i2c-amd-mp2-pci

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
cat "/proc/acpi/wakeup" > "${DIR}/wakeup.txt"
cat "/proc/cpuinfo" > "${DIR}/cpuinfo.txt"

decode-dimms &> "${DIR}/dimms.txt"
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
  if sudo smartctl --all "${DISK}" &> "${DIR}/smartctl/${DISK_NAME}"; then
    echo "Checking smartctl data for ${DISK} failed. Either the drive does not support smartctl or it's failing."
  fi
done

# Python
if command -v pip &> /dev/null; then
  pip -V &> "${DIR}/pip.txt"
  pip list |& tee -a "${DIR}/pip.txt"
else
  echo "pip was not found."
fi

if command -v pip3 &> /dev/null; then
  pip3 -V &> "${DIR}/pip3.txt"
  pip3 list |& tee -a "${DIR}/pip3.txt"
else
  echo "pip3 was not found."
fi

# GPU info
if command -v clinfo &> /dev/null; then
  clinfo &> "${DIR}/clinfo.txt"
else
  echo "clinfo was not found."
fi

if command -v nvidia-smi &> /dev/null; then
  nvidia-smi &> "${DIR}/nvidia-smi.txt"
else
  echo "nvidia-smi was not found. This system probably doesn't have Nvidia GPUs installed."
fi

if command -v rocminfo &> /dev/null; then
  rocminfo &> "${DIR}/rocminfo.txt"
else
  echo "rocminfo was not found."
fi

if command -v rocm-smi &> /dev/null; then
  rocm-smi &> "${DIR}/rocm-smi.txt"
else
  echo "rocm-smi was not found."
fi

if [ "$1" != "--no-report" ]; then
  # Packaging
  7zr a -mx=9 "${DIR}_$(date '+%Y-%m-%d_%H-%M-%S').7z" "${DIR}"
  echo "The report is ready."
fi
