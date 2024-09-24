#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

apt-get update
apt-get --fix-broken install
dpkg --configure -a
update-initramfs -u
update-grub
