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

MOUNTPOINT="/media/${USER}/kale"
if $UMOUNT; then
  fusermount -u "${MOUNTPOINT}/home"
  fusermount -u "${MOUNTPOINT}/proj"
  fusermount -u "${MOUNTPOINT}/wrkdir"
else
  if [ ! -d "${MOUNTPOINT}" ]; then
    sudo mkdir -p "${MOUNTPOINT}/home" "${MOUNTPOINT}/proj" "${MOUNTPOINT}/wrkdir"
    sudo chown "${USER}" "${MOUNTPOINT}/home" "${MOUNTPOINT}/proj" "${MOUNTPOINT}/wrkdir"
  fi
  . "./config.sh"
  HOST_STR="${KALE_USERNAME}@kale.grid.helsinki.fi"
  sshfs "${HOST_STR}:/home/${KALE_USERNAME}" "${MOUNTPOINT}/home"
  sshfs "${HOST_STR}:/proj/${KALE_USERNAME}" "${MOUNTPOINT}/proj"
  sshfs "${HOST_STR}:/wrk/users/${KALE_USERNAME}" "${MOUNTPOINT}/wrkdir"
fi
