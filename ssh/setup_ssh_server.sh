#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

echo "Installing SSH server."
apt update
apt install openssh-server

echo "Disabling password login."
sed -i "s@#PasswordAuthentication yes@PasswordAuthentication no@g" "/etc/ssh/sshd_config"
systemctl restart ssh

if command -v &> /dev/null; then
  echo "Creating UFW firewall rule and enabling UFW."
  ufw allow ssh comment SSH
  ufw enable
else
  echo "UFW was not found."
fi
