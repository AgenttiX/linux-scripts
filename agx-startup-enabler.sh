#!/usr/bin/env sh
cp ./agx-startup.service /etc/systemd/system/
cp ./agx-startup.py /usr/local/bin/
chown root:root /etc/systemd/system/agx-startup.service
chown root:root /usr/local/bin/agx-startup.py
chmod 644 /etc/systemd/system/agx-startup.service
chmod 755 /usr/local/bin/agx-startup.py
systemctl daemon-reload
systemctl enable agx-startup.service
