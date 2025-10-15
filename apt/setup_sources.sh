#!/usr/bin/env bash
set -eu
# Setup sources

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

mkdir -p /etc/apt/keyrings
apt update
apt install apt-transport-https ca-certificates curl gpg-agent ubuntu-dbgsym-keyring wget

# -----
# Ubuntu repos
# -----

# Debug symbols
# https://documentation.ubuntu.com/server/explanation/debugging/debug-symbol-packages/
echo "Types: deb
URIs: http://ddebs.ubuntu.com/
Suites: $(lsb_release -cs) $(lsb_release -cs)-updates $(lsb_release -cs)-proposed
Components: main restricted universe multiverse
Signed-by: /usr/share/keyrings/ubuntu-dbgsym-keyring.gpg" | \
sudo tee /etc/apt/sources.list.d/ddebs.sources

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

# eduVPN
wget -O- https://app.eduvpn.org/linux/v4/deb/app+linux@eduvpn.org.asc | gpg --dearmor | tee /usr/share/keyrings/eduvpn-v4.gpg >/dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/eduvpn-v4.gpg] https://app.eduvpn.org/linux/v4/deb/ plucky main" | tee /etc/apt/sources.list.d/eduvpn-v4.list

# Intel oneAPI
# https://www.intel.com/content/www/us/en/developer/tools/oneapi/hpc-toolkit-download.html
wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list

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

apt update
