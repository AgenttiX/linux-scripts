#!/bin/bash -e
# https://wiki.archlinux.org/title/Solid_state_drive/Memory_cell_clearing

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

DISK=$1
if ! [ -e "${DISK}" ]; then
  echo "Please supply a valid disk as the only argument."
  exit 1
fi

HDPARM_OUTPUT=$(hdparm -I "${DISK}")

if ! (grep "frozen" <<< "${HDPARM_OUTPUT}"); then
  echo "The disk security status could not be determined."
  exit 1
fi

if ! ( (grep "frozen" <<< "${HDPARM_OUTPUT}") | grep "not"); then
  echo "The disk security seems to be frozen."
  exit 1
fi

if ! ( (grep "enabled" <<< "${HDPARM_OUTPUT}") | grep "not"); then
  echo "The disk security seems to be already enabled. The operation may not work."
fi

read -p "Are you sure you want to clear the drive ${DISK}? THIS WILL DESTROY ALL DATA!" -n 1 -r
echo
if ! [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "The operation was cancelled by the user."
  exit 0
fi

# This password will be removed by the erasure, so it doesn't have to be secret.
SSD_PASSWORD="uKdPVuSNyq7q"
hdparm --user-master u --security-set-pass "${SSD_PASSWORD}" "${DISK}"

# Todo: Test the detection of enhanced erase with a compatible SSD.
if (grep "        supported: enhanced erase" <<< "${HDPARM_OUTPUT}"); then
  echo "Erasing the drive with enhanced erase."
  hdparm --user-master u --security-erase-enhanced "${SSD_PASSWORD}" "${DISK}"
else
  echo "Erasing the drive with basic erase."
  hdparm --user-master u --security-erase "${SSD_PASSWORD}" "${DISK}"
fi
