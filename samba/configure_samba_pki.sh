#!/usr/bin/env bash
set -e

# Configure an Active Directory Certificate Services client.
# https://wiki.samba.org/index.php/Certificate_Auto_Enrollment

# Before running this script, install and configure the DC and CA:
# https://github.com/openSUSE/cepces/wiki/Scenarios
# If your CA is on a DC, you may encounter issues in using the svc_cepces account as the service account for CES.
# Do not add it to the Administrators or domain admins group!
# Instead, add it at most to Server Operators.
# https://www.petenetlive.com/KB/Article/0001242

# TODO: After the configuration, the CEP server is still giving this error:
# 401 - Unauthorized: Access is denied due to invalid credentials.

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi

if [ $# -ne 2 ]; then
  echo "Please give the CA name, e.g. \"company\", and the CA FQDN, e.g. \"ca.company.com\", as arguments."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
# GIT_DIR="$(dirname "${REPO_DIR}")"

. "${REPO_DIR}/github.sh"

sudo apt-get update
# First line: direct dependencies
# Second line: build dependencies
sudo apt-get install \
  certmonger python3-cryptography python3-requests python3-requests-kerberos wget \
  autoconf automake ldb-tools libkrb5-dev libssl-dev libtool make pkgconf python3-pip
# Python 3.11 does not allow installing packages globally by default,
# and requests_gssapi is not available with apt-get.
sudo pip3 install requests_gssapi --break-system-packages

# These need wget, which is installed above.
CEPCES_RELEASE="$(get_latest_release "openSUSE/cepces")"
CEPCES_RELEASE_NUMBER="${CEPCES_RELEASE:1}"
CEPCES_DIR="${SCRIPT_DIR}/cepces/cepces-${CEPCES_RELEASE_NUMBER}"
CEPCES_CONF_DIR="/etc/cepces"
SSCEP_RELEASE="$(get_latest_release "certnanny/sscep")"
SSCEP_RELEASE_NUMBER="${SSCEP_RELEASE:1}"
SSCEP_DIR="${SCRIPT_DIR}/sscep/sscep-${SSCEP_RELEASE_NUMBER}"
CERT_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
KEYTAB="/etc/krb5.keytab"
CA_NAME=$1
CA_SERVER=$2

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

# https://github.com/openSUSE/cepces/wiki/Scenarios#configure-cepces
echo "Manually placing the cepces files to folders where they are automatically found."
sudo cp "${CEPCES_DIR}/bin/cepces-submit" "/usr/lib/certmonger/cepces-submit"
sudo mkdir -p "${CEPCES_CONF_DIR}"
sudo mkdir -p "/var/log/cepces"
sudo cp "${CEPCES_DIR}/conf/cepces.conf.dist" "${CEPCES_CONF_DIR}/cepces.conf"
sudo cp "${CEPCES_DIR}/conf/logging.conf.dist" "${CEPCES_CONF_DIR}/logging.conf"
echo "cepces installation ready."
echo "Configuring cepces."
sudo sed -i "s/^#cas=.*/cas=${CERT_BUNDLE}"

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

SECRETS_LDB="/var/lib/samba/private/secrets.ldb"
if [ ! -f "${SECRETS_LDB}" ]; then
  echo "${SECRETS_LDB} does not exist. Creating an empty one to avoid Samba error messages."
  echo "https://bugzilla.samba.org/show_bug.cgi?id=14657"
  sudo ldbadd -H "${SECRETS_LDB}" </dev/null
fi

if [ ! -f "${KEYTAB}" ]; then
  echo "Kerberos keytab does not exist. Creating."
  # https://runops.wordpress.com/2015/04/22/create-machine-keytab-on-linux-for-active-directory-authentication/
  # https://wiki.samba.org/index.php/Keytab_Extraction#Online_Keytab_Creation_from_Machine_Account_Password
  KRB5_KTNAME="FILE:${KEYTAB}" sudo net ads keytab CREATE -P
fi

if sudo getcert list-cas | grep -q "cepces"; then
  echo "Removing old cepces CA."
  sudo getcert remove-ca -c cepces
fi
echo "Adding cepces CA."
sudo getcert add-ca -c cepces -e "/usr/lib/certmonger/cepces-submit"
echo "Installed CAs:"
sudo getcert list-cas

echo "Fetching CA certificate."
CA_CERT="/usr/local/share/ca-certificates/${CA_NAME}-ca.crt"
# https://serverfault.com/a/800979
# This does not work yet. You have to go to https://<CA_CERVER_NAME>/certsrv to fetch the certificate manually.
echo | openssl s_client -servername "${CA_SERVER}" -connect "${CA_SERVER}:443" | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' | sudo tee "${CA_CERT}"
echo "Found certificate:"
cat "${CA_CERT}"
# The certificates go to /etc/ssl/certs/ca-certificates.crt
sudo update-ca-certificates

echo "Restarting certmonger"
sudo systemctl restart certmonger.service
echo "certmonger restarted."
sudo systemctl status certmonger.service

echo "Restarting smbd."
sudo systemctl restart smbd.service
echo "smbd restarted."
sudo systemctl status smbd.service

echo "Updating group policies."
sudo samba-gpudpate --rsop --machine-pass

echo "Installed certificates:"
sudo getcert list
