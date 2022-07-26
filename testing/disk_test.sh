#!/bin/bash -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

# Storage devices
if command -v smartctl &> /dev/null; then
  mapfile -t SMARTCTL_SCAN < <(smartctl --scan)
  for LINE in "${SMARTCTL_SCAN[@]}"; do
    IFS=", " read -r -a ARR <<< "${LINE}"
    DISK="${ARR[0]}"
    DISK_NAME="$(basename "${DISK}")"
    echo "Starting long SMART test on ${DISK_NAME}"
    sudo smartctl --test=long "${DISK}"
  done
else
  echo "The command \"smartctl\" was not found."
fi
