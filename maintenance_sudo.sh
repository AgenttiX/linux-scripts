#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

apt-get update
apt-get dist-upgrade -y
apt-get autoremove -y
apt-get autoclean -y
python3 ./maintenance.py
