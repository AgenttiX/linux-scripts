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
sudo apt-get install p7zip
echo "The following packages will enable additional reporting. Please install them if you can."
set +e
sudo apt-get install acpi clinfo dmidecode i2c-tools lshw lsscsi vainfo vdpauinfo
# Load kernel modules for decode-dimms
# https://superuser.com/a/1499521/
if command -v decode-dimms &> /dev/null; then
  sudo modprobe at24
  sudo modprobe ee1004
  sudo modprobe eeprom
  sudo modprobe i2c-i801
  sudo modprobe i2c-amd-mp2-pci
fi
set -e

mkdir -p "${DIR}"
# Remove old results
if [ "$(ls -A $DIR)" ]; then
  rm -r "${DIR:?}"/*
fi
mkdir -p "${DIR}/hdparm" "${DIR}/smartctl"

# Basic info
echo -n "Hostname: "
hostname |& tee "${DIR}/basic.txt"
echo -n "Uname: "
uname -a |& tee -a "${DIR}/basic.txt"
echo "HDDs" |& tee -a "${DIR}/basic.txt"
smartctl --scan |& tee -a "${DIR}/basic.txt"

function report_command () {
  if [ "${1}" = "sudo" ]; then
    if command -v "${2}" &> /dev/null; then
      # shellcheck disable=SC2024
      sudo "${@:2}" &> "${DIR}/${2}.txt"
    else
      echo "The command \"${2}\" was not found."
    fi
  else
    if command -v "${1}" &> /dev/null; then
      ${1} "${@:2}" &> "${DIR}/${1}.txt"
    else
      echo "The command \"${1}\" was not found."
    fi
  fi
}

# Root info
# These should be first so that the probability of having to ask sudo password again is minimized.

report_command sudo dmesg
report_command sudo dmidecode
if command -v docker &> /dev/null; then
  {
    sudo docker -v
    sudo docker system info
    sudo docker image ls
    sudo docker container ls
  } &> "${DIR}/docker.txt"
else
  echo "The command \"docker\" was not found."
fi
if command -v lshw &> /dev/null; then
  # shellcheck disable=SC2024
  sudo lshw -html > "${DIR}/lshw.html"
else
  echo "The command \"lshw\" was not found."
fi
# Storage devices
if command -v smartctl &> /dev/null; then
  mapfile -t SMARTCTL_SCAN < <(smartctl --scan)
  for LINE in "${SMARTCTL_SCAN[@]}"; do
    IFS=', ' read -r -a ARR <<< "${LINE}"
    DISK="${ARR[0]}"
    DISK_NAME="$(basename "${DISK}")"
    # shellcheck disable=SC2024
    sudo hdparm -I "${DISK}" &> "${DIR}/hdparm/${DISK_NAME}.txt"
    # shellcheck disable=SC2024
    if sudo smartctl --all "${DISK}" &> "${DIR}/smartctl/${DISK_NAME}.txt"; then
      echo "Checking smartctl data for ${DISK} failed. Either the drive does not support smartctl or it's failing."
    fi
  done
else
  echo "The command \"smartctl\" was not found."
fi
# Non-root info

cat "/proc/acpi/wakeup" > "${DIR}/wakeup.txt"
cat "/proc/cpuinfo" > "${DIR}/cpuinfo.txt"
cat "/var/log/syslog" > "${DIR}/syslog.txt"

report_command acpi --everything --details
report_command clinfo
report_command decode-dimms
report_command lsblk
report_command lscpu
report_command lspci
report_command lsscsi
report_command lsusb
report_command nvidia-smi
# Battery info
if command -v upower &> /dev/null; then
  {
    upower --enumerate
    upower --dump
    upower --wakeups
  } &> "${DIR}/upower.txt"
else
  echo "The command \"upower\" was not found."
fi
# Python
if command -v pip &> /dev/null; then
  {
    pip -V
    pip list
  } &> "${DIR}/pip.txt"
else
  echo "Python pip was not found."
fi
if command -v pip3 &> /dev/null; then
  {
    pip3 -V
    pip3 list
  } &> "${DIR}/pip3.txt"
else
  echo "Python pip3 was not found."
fi
report_command rocminfo
report_command rocm-smi
report_command vainfo
report_command vdpauinfo
report_command xinput list
report_command xrandr

if [ "$1" != "--no-report" ]; then
  # Packaging
  7zr a -mx=9 "${DIR}_$(date '+%Y-%m-%d_%H-%M-%S').7z" "${DIR}"
  echo "The report is ready."
fi
