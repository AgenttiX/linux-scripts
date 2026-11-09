#!/usr/bin/env bash
set -e

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

sed -i "s@#PasswordAuthentication yes@PasswordAuthentication no@g" "/etc/ssh/sshd_config"
