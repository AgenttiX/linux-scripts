#!/usr/bin/env bash
set -e

# https://wiki.archlinux.org/title/Lenovo_ThinkPad_T480

# Fingerprint: Python-validity
# https://www.reddit.com/r/thinkpad/comments/ja661k/t480_linux_users_rejoice_the_fingerprint_scanner/
# https://github.com/uunicorn/python-validity
# https://www.reddit.com/r/thinkpad/comments/ibcpob/fingerprint_works_on_t480_kernel_581/

# Monitoring: s-tui
# https://github.com/amanusk/s-tui

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WORKDIR="$(pwd)"

sudo apt-get remove fprintd
sudo add-apt-repository ppa:uunicorn/open-fprintd
sudo apt-get update

# Lines are:
# - generic
# - throttled
# - python-validity
# - s-tui
sudo apt-get install git \
  build-essential python3-dev libdbus-glib-1-dev libgirepository1.0-dev libcairo2-dev python3-cairo-dev python3-venv python3-wheel \
  open-fprintd fprintd-clients python3-validity \
  s-tui stress

echo "Configuring psmouse (touchpad refresh rate)"
sudo cp "${SCRIPT_DIR}/psmouse.conf" "/etc/modprobe.d/"
sudo chown root:root "/etc/modprobe.d/psmouse.conf"
sudo chmod 644 "/etc/modprobe.d/psmouse.conf"
echo "psmouse configured"

# https://github.com/erpalma/throttled
echo "Installing Throttled"
mkdir -p "${HOME}/Git"
cd "${HOME}/Git"
if [ -d "${HOME}/Git/throttled" ] {
  cd "${HOME}/Git/throttled"
  git pull
} else {
  git clone https://github.com/erpalma/throttled.git
  cd "${HOME}/Git/throttled"
}
sudo ./install.sh

cd "${WORKDIR}"

# Enable fingerprint authentication here. No need to change the other settings.
sudo pam-auth-update
