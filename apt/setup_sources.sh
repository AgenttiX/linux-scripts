#!/usr/bin/env bash
set -eu
# Setup sources

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

mkdir -p /etc/apt/keyrings
apt-get update
apt-get install apt-transport-https ca-certificates curl ubuntu-dbgsym-keyring

# -----
# Ubuntu repos
# -----

# Debug symbols
# https://ubuntu.com/server/docs/debug-symbol-packages
echo "deb http://ddebs.ubuntu.com $(lsb_release -cs) main restricted universe multiverse
deb http://ddebs.ubuntu.com $(lsb_release -cs)-updates main restricted universe multiverse
deb http://ddebs.ubuntu.com $(lsb_release -cs)-proposed main restricted universe multiverse" | \
sudo tee -a /etc/apt/sources.list.d/ddebs.list

# -----
# Custom repos in alphabetical order
# -----

# Docker
# https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Nvidia CUDA
. "$(dirname "${SCRIPT_DIR}")/drivers/setup_nvidia_repos.sh"

# Signal
# https://signal.org/download/
wget -O- https://updates.signal.org/desktop/apt/keys.asc | gpg --dearmor > signal-desktop-keyring.gpg
cat signal-desktop-keyring.gpg | tee /usr/share/keyrings/signal-desktop-keyring.gpg > /dev/null
# The distro name has been "xenial" for quite a while
echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/signal-desktop-keyring.gpg] https://updates.signal.org/desktop/apt xenial main' |\
  tee /etc/apt/sources.list.d/signal-xenial.list

# Syncthing
# https://apt.syncthing.net/
curl -L -o /etc/apt/keyrings/syncthing-archive-keyring.gpg https://syncthing.net/release-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable" | tee /etc/apt/sources.list.d/syncthing.list

# Speedtest
# curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash

# TeamViewer
if command -v teamviewer &> /dev/null; then
  sudo teamviewer repo default
fi

# -----
# PPAs
# -----
# For OpenTabletDriver dotnet-runtime-6.0 dependency
# https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu#register-the-ubuntu-net-backports-package-repository
# add-apt-repository ppa:dotnet/backports
# add-apt-repository ppa:linuxuprising/java
# add-apt-repository ppa:obsproject/obs-studio
add-apt-repository ppa:phoerious/keepassxc
# add-apt-repository ppa:thopiekar/openrgb
if [ "$(hostnamectl chassis)" = "laptop" ]; then
  echo "This seems to be a laptop. Enabling the TLP and Touchegg repositories."
  add-apt-repository ppa:linrunner/tlp
  add-apt-repository ppa:touchegg/stable
else
  echo "This does not seem to be a laptop. Skipping Touchegg and TLP repository setup."
fi

apt-get update
