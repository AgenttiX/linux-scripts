#!/usr/bin/env bash
set -e

# Configure an Active Directory Certificate Services client.

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
GIT_DIR="$(dirname "${REPO_DIR}")"

. "${REPO_DIR}/github.sh"

sudo apt-get update
# First line: direct dependencies
# Second line: build dependencies
sudo apt-get install \
  certmonger python3-cryptography python3-requests python3-requests-kerberos wget \
  autoconf automake libtool libssl-dev make pkgconf

# These need wget, which is installed above.
CEPCES_RELEASE="$(get_latest_release "openSUSE/cepces")"
CEPCES_RELEASE_NUMBER="${CEPCES_RELEASE:1}"
CEPCES_DIR="${SCRIPT_DIR}/cepces/cepces-${CEPCES_RELEASE_NUMBER}"
SSCEP_RELEASE="$(get_latest_release "certnanny/sscep")"
SSCEP_RELEASE_NUMBER="${SSCEP_RELEASE:1}"
SSCEP_DIR="${SCRIPT_DIR}/sscep/sscep-${SSCEP_RELEASE_NUMBER}"

echo "Downloading cepces."
mkdir -p "${SCRIPT_DIR}/cepces"
if ! [ -d "${CEPCES_DIR}" ]; then
  download_release_source "openSUSE/cepces" "${CEPCES_RELEASE}" "tar.gz" "${SCRIPT_DIR}/cepces/cepces-${CEPCES_RELEASE_NUMBER}.tar.gz"
  tar -xvzf "${CEPCES_DIR}.tar.gz" -C "${SCRIPT_DIR}/cepces"
fi
cd "${CEPCES_DIR}"

echo "Installing cepces."
# All the requirements are provided by apt
# pip3 install -r requirements.txt
sudo python3 setup.py install
echo "cepces installation ready."

echo "Downloading sscep."
mkdir -p "${SCRIPT_DIR}/sscep"
if ! [ -d "${SSCEP_DIR}" ]; then
  download_release_source "certnanny/sscep" "${SSCEP_RELEASE}" "tar.gz" "${SCRIPT_DIR}/sscep/sscep-${SSCEP_RELEASE_NUMBER}.tar.gz"
  tar -xvzf "${SSCEP_DIR}.tar.gz" -C "${SCRIPT_DIR}/sscep"
fi
cd "${SSCEP_DIR}"

echo "Bootstrapping sscep installation."
./bootstrap.sh
echo "Configuring sscep installation."
./configure
echo "Making sscep."
make
echo "Installing sscep."
sudo make install
echo "sscep installation ready."

echo "Restarting smbd.service."
sudo systemctl restart smbd.service
echo "smbd.service restarted."
sudo systemctl status smbd.service
