#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

apt update
apt dist-upgrade -y
apt autoremove -y
apt autoclean -y
python3 ./maintenance.py
