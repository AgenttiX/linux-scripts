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

if command -v mortar-compilesigninstall &> /dev/null; then
  HAS_MORTAR=true
else
  HAS_MORTAR=false
fi

if [ "${HAS_MORTAR}" = "true" ]; then
  echo "Configuring DKMS to use the Mortar MOK key."
  sed -i 's@^# mok_signing_key=/var/lib/dkms/mok.key@mok_signing_key="/etc/mortar/private/db.key"@g; s@^# mok_certificate=/var/lib/dkms/mok.pub@mok_certificate="/etc/mortar/private/db.crt"@g' "/etc/dkms/framework.conf"
else
  echo "Currently enrolled MOK keys:"
  mokutil --list-enrolled
  echo "Configuring MOK for DKMS kernel modules."
  update-secureboot-policy --enroll-key
  echo "New MOK keys:"
  mokutil --list-new
fi

echo "Updating initramfs."
update-initramfs -u

if [ "${HAS_MORTAR}" = "true" ]; then
  echo "Running mortar-compilesigninstall to update the EFI file."
  mortar-compilesigninstall
  echo "DKMS MOK configuration ready. You should now reboot."
else
  echo "Updating GRUB configuration."
  update-grub
  echo "DKMS MOK configuration ready. You should now reboot and then input the MOK password to enroll the key."
fi
