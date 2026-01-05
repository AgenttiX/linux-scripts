#!/bin/bash -e

# This script configures the Machine Owner Key (MOK) for the UEFI Secure Boot
# so that DKMS kernel modules work properly.
# https://wiki.ubuntu.com/UEFI/SecureBoot
# https://wiki.debian.org/SecureBoot
# https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

echo "Configuring MOK for DKMS kernel modules."
update-secureboot-policy --enroll-key
echo "Updating initramfs."
update-initramfs -u

if command -v mortar-compilesigninstall &> /dev/null; then
  echo "Mortar detected. Running mortar-compilesigninstall."
  mortar-compilesigninstall
else
  echo "Updating GRUB configuration."
  update-grub
fi
