#!/usr/bin/env bash
set -eu

# https://wiki.rpcs3.net/index.php?title=Help:Controller_Configuration#On_Linux

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

apt-get update
# You may also want to install bluez-tools, but in my experience it's not necessary.
apt-get install bluez

echo "Copying udev rules."
cp "${SCRIPT_DIR}/99-ds3-controllers.rules" "/etc/udev/rules.d/99-ds3-controllers.rules"
cp "${SCRIPT_DIR}/99-ds4-controllers.rules" "/etc/udev/rules.d/99-ds4-controllers.rules"
chmod 644 "/etc/udev/rules.d/99-ds3-controllers.rules" "/etc/udev/rules.d/99-ds4-controllers.rules"
echo "Reloading udev rules."
udevadm control --reload-rules

echo "Enabling PS3 controller pairing without PIN."
# https://www.reddit.com/r/linux_gaming/comments/18p5mqu/ps3_controller_pin/
# https://askubuntu.com/questions/1497783/why-does-official-ps3-bluetooth-controller-no-longer-work-and-pin-code-suddenly
sed -i "s/#ClassicBondedOnly=true/ClassicBondedOnly=false/g" "/etc/bluetooth/input.conf"

echo "Restarting the Bluetooth service."
systemctl restart bluetooth

echo "DualShock setup complete."
