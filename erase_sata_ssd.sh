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
  echo "This is probably caused by the BIOS, and suspending to S3 may fix this."
  echo "If this is a Lenovo laptop, you may have to use their proprietary tool that you can find from the driver downloads."
  echo "Note that you may have to burn the utility to a physical CD, as a USB drive may not work."
  echo "https://superuser.com/a/763740/"
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
echo "Setting SSD password to unlock erasing."
echo "DO NOT REBOOT THE COMPUTER! Some laptop BIOS versions, especially Lenovo, may mess with this password resulting in a bricked SSD!"
echo "https://jbeekman.nl/blog/2015/03/lenovo-thinkpad-hdd-password/"
echo "https://github.com/jethrogb/lenovo-password"
hdparm --user-master u --security-set-pass "${SSD_PASSWORD}" "${DISK}"

# Todo: Test the detection of enhanced erase with a compatible SSD.
if (grep "        supported: enhanced erase" <<< "${HDPARM_OUTPUT}"); then
  echo "Erasing the drive with enhanced erase."
  hdparm --user-master u --security-erase-enhanced "${SSD_PASSWORD}" "${DISK}"
else
  echo "Erasing the drive with basic erase."
  hdparm --user-master u --security-erase "${SSD_PASSWORD}" "${DISK}"
fi

echo "Erase has been started successfully. The drive security should now be reset."
echo "The drive status is:"
hdparm -I "${DISK}"
