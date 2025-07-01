#!/bin/bash -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

if ! (command -v smartctl &> /dev/null); then
  echo "smartmontools seems not to be installed. Installing."
  sudo apt install smartmontools
fi

# Storage devices
if command -v smartctl &> /dev/null; then
  mapfile -t SMARTCTL_SCAN < <(smartctl --scan)
  for LINE in "${SMARTCTL_SCAN[@]}"; do
    IFS=", " read -r -a ARR <<< "${LINE}"
    DISK="${ARR[0]}"
    DISK_NAME="$(basename "${DISK}")"
    echo "#####"
    echo "# Starting long SMART test on ${DISK_NAME}"
    echo "#####"
    sudo smartctl --test=long "${DISK}"
    echo
  done
else
  echo "The command \"smartctl\" was not found."
fi
