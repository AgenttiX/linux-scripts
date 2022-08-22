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

update-secureboot-policy --enroll-key
update-initramfs -u
update-grub
