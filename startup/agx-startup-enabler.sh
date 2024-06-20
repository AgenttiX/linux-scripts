#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

echo "Installing the agx-startup script"
cp ./agx-startup.service /etc/systemd/system/
mkdir -p /usr/local/bin/agx
cp ./agx_startup.py /usr/local/bin/agx/
chown root:root /etc/systemd/system/agx-startup.service
chown root:root /usr/local/bin/agx/agx_startup.py
chmod 644 /etc/systemd/system/agx-startup.service
chmod 755 /usr/local/bin/agx/agx_startup.py
systemctl daemon-reload
systemctl enable agx-startup.service
# Remove old script versions
rm -f /usr/local/bin/agx_startup.py
echo "Installation ready"
