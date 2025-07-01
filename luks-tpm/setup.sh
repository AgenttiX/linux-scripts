#!/bin/bash -e
# This script enables automatic TPM-based unlocking of the LUKS encrypted
# root partition with a fallback to password query.

# This script has been tested to work with Ubuntu, but it's rather rudimentary,
# and may require manually inputting the password after a kernel upgrade.
# You should probably use Mortar instead.
# https://github.com/noahbliss/mortar

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

apt update
apt install -y tpm2-initramfs-tool
read -s -p "Please input the current LUKS passphrase:" luks_passphrase
echo
tpm2-initramfs-tool seal --data "$luks_passphrase"
echo
cp ./tpm2-initramfs-tool /etc/initramfs-tools/hooks/
cp ./tpm2-initramfs-script /bin/
chown root:root /etc/initramfs-tools/hooks/tpm2-initramfs-tool
chown root:root /usr/bin/tpm2-initramfs-script
chmod 755 /etc/initramfs-tools/hooks/tpm2-initramfs-tool
chmod 755 /usr/bin/tpm2-initramfs-script
echo "Checking that the script works"
/usr/bin/tpm2-initramfs-script
echo
echo "Now edit /etc/crypttab and append \",keyscript=/usr/bin/tpm2-initramfs-script\" to the root disk configuration."
echo "Then run \"update-initramfs -u\" to apply the configuration."
