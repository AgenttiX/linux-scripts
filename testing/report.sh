#!/bin/bash

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
LM_SENSORS_INSTALLED=$(command -v sensors &> /dev/null)
# set +e
if sudo apt-get update; then
  echo "Updating repository data failed. Are there expired signing keys or missing Release files?"
fi
if sudo apt-get install p7zip; then
  echo "Failed to install p7zip. Compressing the final report may not work."
fi
echo "The following packages will enable additional reporting. Please install them if you can."
sudo apt-get install acpi clinfo dmidecode i2c-tools lm-sensors lshw lsscsi vainfo vdpauinfo vulkan-tools
# Load kernel modules for decode-dimms
# https://superuser.com/a/1499521/
if command -v decode-dimms &> /dev/null; then
  sudo modprobe at24
  sudo modprobe ee1004
  sudo modprobe eeprom
  sudo modprobe i2c-i801
  sudo modprobe i2c-amd-mp2-pci
fi
# set -e
# It's not clear whether this should be before or after loading the kernel modules.
# As this is after loading them, it could detect more devices, but on the other hand
# it might be unsafe.
# TODO: test that this works
if (command -v sensors &> /dev/null) && [ "${LM_SENSORS_INSTALLED}" -ne 1 ]; then
  echo "lm-sensors was installed with this run of the script."
  echo "Therefore the sensors haven't been configured yet and should be configured now."
  sudo sensors-detect
fi

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
if command -v smartctl &> /dev/null; then
  smartctl --scan |& tee -a "${DIR}/basic.txt"
else
  echo "The command \"smartctl\" was not found."
fi

function report_command () {
  if [ "${1}" = "sudo" ]; then
    if command -v "${2}" &> /dev/null; then
      # shellcheck disable=SC2024
      if sudo "${@:2}" &> "${DIR}/${2}.txt"; then :; else
        echo "Running the command \"${*}\" failed."
      fi
    else
      echo "The command \"${2}\" was not found."
    fi
  else
    if command -v "${1}" &> /dev/null; then
      if ${1} "${@:2}" &> "${DIR}/${1}.txt"; then :; else
        echo "Running the command \"${*}\" failed."
      fi
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
    IFS=", " read -r -a ARR <<< "${LINE}"
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
# RAID devices
# This should be after regular HDD/SSD checks so that the individual drives are checked before the higher-level features.
if command -v mdadm &> /dev/null; then
  mapfile -t MDADM_SCAN < <(sudo mdadm --detail --scan)
  echo "${MDADM_SCAN[@]}"
  for LINE in "${MDADM_SCAN[@]}"; do
    IFS=" " read -r -a ARR <<< "${LINE}"
    # shellcheck disable=SC2024
    sudo mdadm --detail "${ARR[1]}" &>> "${DIR}/mdadm.txt"
  done
else
  echo "The command \"mdadm\" was not found."
fi

# Non-root info

cat "/proc/acpi/wakeup" > "${DIR}/wakeup.txt"
cat "/proc/cpuinfo" > "${DIR}/cpuinfo.txt"
cat "/proc/mdstat" > "${DIR}/mdstat.txt"
cat "/var/log/syslog" > "${DIR}/syslog.txt"

report_command acpi --everything --details
report_command clinfo
report_command decode-dimms
report_command df --human-readable
report_command lsblk
report_command lsb_release -a
report_command lscpu
report_command lsmod
report_command lspci
report_command lsscsi
# lsusb seems to return 1 on virtual servers.
# set +e
report_command lsusb
# set -e
report_command nvidia-smi
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
report_command sensors
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
report_command vainfo
report_command vdpauinfo
report_command vulkaninfo
report_command xinput list
report_command xrandr

if [ -d "/var/log/samba" ] && command -v rsync &> /dev/null; then
  # The cores folder would require root access, so let's skip it.
  rsync -av --progress "/var/log/samba" "${DIR}" --exclude "cores"
fi

if [ "$1" != "--no-report" ]; then
  # Packaging
  7zr a -mx=9 "${DIR}_$(date '+%Y-%m-%d_%H-%M-%S').7z" "${DIR}"
  echo "The report is ready."
fi
