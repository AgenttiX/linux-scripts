#!/bin/bash -e
# This script configures the configuration script to be run when plugging in the tablet.

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TABLET_USER="${USER}"

sudo apt-get install python3-xlib
echo "Installing the launcher."
sudo cp ./99-wacom-tablet*.rules "/etc/udev/rules.d/"
sudo cp "./wacom.sh" "/usr/local/bin/"
sudo chown root:root /etc/udev/rules.d/99-wacom-tablet*.rules "/usr/local/bin/wacom.sh"
sudo chmod 0644 /etc/udev/rules.d/99-wacom-tablet*.rules
sudo chmod 0755 "/usr/local/bin/wacom.sh"

# Replace the placeholder variables in the script
sudo sed -i "s+USERNAME+${TABLET_USER}+g; s+SCRIPT_DIR+${SCRIPT_DIR}+g" "/usr/local/bin/wacom.sh"

sudo udevadm control --reload-rules
echo "Launcher installed."
