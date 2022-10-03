#!/usr/bin/env bash
set -e

# Attempt to fix issues with Samba and show current configs.

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

testparm --suppress-prompt
samba-gpupdate --rsop
echo "Certificates:"
ls /var/lib/samba/certs
