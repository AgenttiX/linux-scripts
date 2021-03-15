#!/bin/sh -e
apt-get install python3-xlib
cp ./99-wacom-tablet.rules /etc/udev/rules.d/
chown root:root /etc/udev/rules.d/99-wacom-tablet.rules
chmod 644 /etc/udev/rules.d/99-wacom-tablet.rules
