#!/usr/bin/env bash
set -e

# Attempt to fix issues with Samba and show current configs.

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

echo "Presence of extended ACL support:"
smbd -b | grep HAVE_LIBACL
echo "Samba configuration:"
testparm --suppress-prompt
echo "Updating group policies."
samba-gpupdate --rsop
if command -v getcert &> /dev/null; then
  echo "CAs:"
  getcert list-cas
else
  echo "Certmonger was not found."
fi
echo "Certificates:"
ls /var/lib/samba/certs
echo "Winbindd ping:"
wbinfo --ping-dc
echo "Kerberos tickets:"
klist
