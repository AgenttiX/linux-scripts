#!/bin/bash
set -e
apt-get update
apt-get install -y tpm2-initramfs-tool
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
