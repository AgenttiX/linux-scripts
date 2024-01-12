#!/usr/bin/env bash
set -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

if [ $# -eq 1 ]; then
  DEVICE="/dev/sr0"
elif [ $# -eq 2 ]; then
  DEVICE=$1
else
  echo "Invalid number of arguments."
  exit 1
fi
FILENAME=$1

if [ $(command -v ddrescue &> /dev/null) -or $(command -v 7zr &> /dev/null) ]; then :; else
  echo "The necessary packages appear not to be installed. Installing."
  sudo apt-get update
  sudo apt-get install gddrescue p7zip
fi

ddrescue -b 2048 -n -v "${DEVICE}" "${FILENAME}.iso" rescue.log
mv rescue.log "${FILENAME}-rescue.log"
sha256sum "${FILENAME}.iso" > "${FILENAME}.iso.sha256"
7zr a -mx=9 "${FILENAME}.7z" "${FILENAME}.iso" "${FILENAME}.iso.sha256"
