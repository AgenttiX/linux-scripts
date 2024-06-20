#!/usr/bin/env bash
set -eu

# https://www.commandlinefu.com/commands/view/10958/unmount-all-cifs-drives

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

for DRIVE in $(mount -lt cifs | sed 's/.*on \(\/.\+\) type.*/\1/') do
  echo "Unmounting ${DRIVE}"
  umount "${DRIVE}"
  umount -l "${DRIVE}"
done
echo "All CIFS network shares are now unmounted."
