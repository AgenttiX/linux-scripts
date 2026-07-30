#!/usr/bin/env bash
set -euo pipefail
# Setup sources

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

set +u
if [ ! -z "${XDG_CURRENT_DESKTOP}" ]; then
  IS_DESKTOP=true
else
  IS_DESKTOP=false
fi
set -u

ARCH="$(dpkg --print-architecture)"
CHASSIS="$(hostnamectl chassis)"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"

download_key() {
  # Download a GPG key
  # The shorthand for the curl options is -fsSL
  curl --fail --silent --show-error --location "$1" | gpg --dearmor --yes -o "$2"
}

mkdir -p /etc/apt/keyrings
apt update
apt install apt-transport-https ca-certificates curl gpg-agent ubuntu-dbgsym-keyring

# -----
# Ubuntu repos
# -----

# Debug symbols
# https://documentation.ubuntu.com/server/explanation/debugging/debug-symbol-packages/
echo "Types: deb
URIs: http://ddebs.ubuntu.com/
Suites: $(lsb_release -cs) $(lsb_release -cs)-updates $(lsb_release -cs)-proposed
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-dbgsym-keyring.gpg" > /etc/apt/sources.list.d/ddebs.sources

# -----
# Custom repos in alphabetical order
# -----
# Claude Desktop
# This package installs its own claude-desktop.list file, which would conflict with this .sources file.
# download_key "https://downloads.claude.ai/claude-desktop/key.asc" /usr/share/keyrings/claude-desktop-archive-keyring.gpg
# echo "Types: deb
# URIs: https://downloads.claude.ai/claude-desktop/apt/stable
# Suites: stable
# Components: main
# Signed-By: /usr/share/keyrings/claude-desktop-archive-keyring.gpg
# Architectures: ${ARCH}" > /etc/apt/sources.list.d/claude-desktop.sources
curl -fsSLo /usr/share/keyrings/claude-desktop-archive-keyring.asc https://downloads.claude.ai/claude-desktop/key.asc
echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/claude-desktop-archive-keyring.asc] https://downloads.claude.ai/claude-desktop/apt/stable stable main" > /etc/apt/sources.list.d/claude-desktop.list

# Docker
# https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
download_key "https://download.docker.com/linux/ubuntu/gpg" /etc/apt/keyrings/docker.gpg
echo "Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Signed-By: /etc/apt/keyrings/docker.gpg
Architectures: ${ARCH}" > /etc/apt/sources.list.d/docker.sources

# Intel oneAPI
# https://www.intel.com/content/www/us/en/developer/tools/oneapi/hpc-toolkit-download.html
download_key "https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB" /usr/share/keyrings/oneapi-archive-keyring.gpg
echo "Types: deb
URIs: https://apt.repos.intel.com/oneapi
Suites: all
Components: main
Signed-By: /usr/share/keyrings/oneapi-archive-keyring.gpg" > /etc/apt/sources.list.d/oneAPI.sources

# Nvidia CUDA
. "${REPO_DIR}/drivers/setup_nvidia_repos.sh"

# Syncthing
# https://apt.syncthing.net/
download_key "https://syncthing.net/release-key.gpg" /etc/apt/keyrings/syncthing-archive-keyring.gpg
echo "Types: deb
URIs: https://apt.syncthing.net/
Suites: syncthing
Components: stable-v2
Signed-By: /etc/apt/keyrings/syncthing-archive-keyring.gpg" > /etc/apt/sources.list.d/syncthing.sources

# Speedtest
# curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash

if [ "${IS_DESKTOP}" = true ]; then
  # eduVPN
  download_key "https://app.eduvpn.org/linux/v4/deb/app+linux@eduvpn.org.asc" /usr/share/keyrings/eduvpn-v4.gpg
  echo "Types: deb
  URIs: https://app.eduvpn.org/linux/v4/deb/
  Suites: plucky
  Components: main
  Signed-By: /usr/share/keyrings/eduvpn-v4.gpg
  Architectures: ${ARCH}" > /etc/apt/sources.list.d/eduvpn-v4.sources

  # Google Antigravity
  download_key "https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg" /etc/apt/keyrings/antigravity-repo-key.gpg
  echo "Types: deb
  URIs: https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/
  Suites: antigravity-debian
  Components: main
  Signed-By: /etc/apt/keyrings/antigravity-repo-key.gpg
  Architectures: ${ARCH}" > /etc/apt/sources.list.d/antigravity.sources

  # Signal
  # https://signal.org/download/
  download_key "https://updates.signal.org/desktop/apt/keys.asc" /usr/share/keyrings/signal-desktop-keyring.gpg
  # The distro name has been "xenial" for quite a while
  echo "Types: deb
  URIs: https://updates.signal.org/desktop/apt
  Suites: xenial
  Components: main
  Signed-By: /usr/share/keyrings/signal-desktop-keyring.gpg
  Architectures: ${ARCH}" > /etc/apt/sources.list.d/signal-xenial.sources

  # TeamViewer
  if command -v teamviewer &> /dev/null; then
    teamviewer repo default
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
    add-apt-repository ppa:touchegg/stable
  fi
fi

if [ "${CHASSIS}" = "laptop" ]; then
  add-apt-repository ppa:linrunner/tlp
fi

apt-get update
