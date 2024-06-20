#!/usr/bin/env bash
set -eu

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

git pull
sudo python3 ./maintenance.py
