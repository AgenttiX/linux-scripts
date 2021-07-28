#!/usr/bin/sh -e

# https://en.wikipedia.org/wiki/Getopts
UMOUNT=false
while getopts "u" FLAG
do
  case "${FLAG}" in
    (u) UMOUNT=true;;
    (*) echo "Unknown flag: ${FLAG}";;
  esac
done

MOUNTPOINT="/media/${USER}/csc"
if $UMOUNT; then
  fusermount -u "${MOUNTPOINT}/home"
else
  if [ ! -d "${MOUNTPOINT}" ]; then
    echo "Mountpoint \"${MOUNTPOINT}\" did not exist. Creating."
    sudo mkdir -p "${MOUNTPOINT}/home"
    sudo chown "${USER}" "${MOUNTPOINT}/home"
  fi
  # Load CSC_USERNAME from config.sh
  . "./config.sh"
  HOST_STR="${CSC_USERNAME}@puhti.csc.fi"
  echo "Mounting home"
  sshfs "${HOST_STR}:/users/${CSC_USERNAME}" "${MOUNTPOINT}/home"
fi
