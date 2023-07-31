#!/usr/bin/env bash
set -e
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

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_DIR="$(dirname "${SCRIPT_DIR}")/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_FILE="${LOG_DIR}/erase_sata_ssd_${TIMESTAMP}.txt"
mkdir -p "${LOG_DIR}"

HDPARM_OUTPUT=$(hdparm -I "${DISK}")
echo "hdparm -I before erase:" &> "${LOG_FILE}"
echo "${HDPARM_OUTPUT}" &>> "${LOG_FILE}"

if ! (grep "frozen" <<< "${HDPARM_OUTPUT}"); then
  echo "The disk security status could not be determined." |& tee -a "${LOG_FILE}"
  exit 1
fi

if ! ( (grep "frozen" <<< "${HDPARM_OUTPUT}") | grep "not"); then
  echo "The disk security seems to be frozen." |& tee -a "${LOG_FILE}"
  echo "This is probably caused by the BIOS, and suspending to S3 may fix this." |& tee -a "${LOG_FILE}"
  echo "If this is a Lenovo laptop, you may have to use their proprietary tool that you can find from the driver downloads." |& tee -a "${LOG_FILE}"
  echo "Note that you may have to burn the utility to a physical CD, as a USB drive may not work." |& tee -a "${LOG_FILE}"
  echo "https://superuser.com/a/763740/" |& tee -a "${LOG_FILE}"
  exit 1
fi

if ! ( (grep "enabled" <<< "${HDPARM_OUTPUT}") | grep "not"); then
  echo "The disk security seems to be already enabled. The operation may not work." |& tee -a "${LOG_FILE}"
fi

read -p "Are you sure you want to clear the drive ${DISK}? THIS WILL DESTROY ALL DATA!" -n 1 -r
echo
if ! [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "The operation was cancelled by the user." |& tee -a "${LOG_FILE}"
  exit 0
fi

# This password will be removed by the erasure, so it doesn't have to be secret.
SSD_PASSWORD="uKdPVuSNyq7q"
echo "Setting SSD password to unlock erasing." |& tee -a "${LOG_FILE}"
echo "DO NOT REBOOT THE COMPUTER! Some laptop BIOS versions, especially Lenovo, may mess with this password resulting in a bricked SSD!" |& tee -a "${LOG_FILE}"
echo "https://jbeekman.nl/blog/2015/03/lenovo-thinkpad-hdd-password/" |& tee -a "${LOG_FILE}"
echo "https://github.com/jethrogb/lenovo-password" |& tee -a "${LOG_FILE}"
hdparm --user-master u --security-set-pass "${SSD_PASSWORD}" "${DISK}" |& tee -a "${LOG_FILE}"

if (grep $'\t\tsupported: enhanced erase' <<< "${HDPARM_OUTPUT}"); then
  echo "Erasing the drive with enhanced erase." |& tee -a "${LOG_FILE}"
  hdparm --user-master u --security-erase-enhanced "${SSD_PASSWORD}" "${DISK}" |& tee -a "${LOG_FILE}"
else
  echo "Erasing the drive with basic erase." |& tee -a "${LOG_FILE}"
  hdparm --user-master u --security-erase "${SSD_PASSWORD}" "${DISK}" |& tee -a "${LOG_FILE}"
fi

echo "Erase has been started successfully. The drive security should now be reset." |& tee -a "${LOG_FILE}"
echo "The drive status is:" |& tee -a "${LOG_FILE}"
hdparm -I "${DISK}" |& tee -a "${LOG_FILE}"
