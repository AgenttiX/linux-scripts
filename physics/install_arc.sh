#!/bin/bash -e

# Todo: this script is not yet complete

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

if ! ([ -f "${HOME}/.globus/certs.p12" ] && [ -f "${HOME}/.globus/usercert.pem" ] && [ -f "${HOME}/.globus/userkey.pem" ]); then
  echo "Copy the certificate files to ~/.globus first."
  exit 1
fi

sudo apt install nordugrid-arc-client voms-clients

USERNAME="TODO-SET-ME-FROM-INPUT"
SERVER="kale.grid.helsinki.fi"

scp "${USERNAME}@${SERVER}:/etc/vomses" "./vomses"
sudo mv ./vomses /etc/vomses
sudo chown root:root /etc/vomses
sudo chmod 644 /etc/vomses

CERT_FILE="NorduGrid-2015.crt"
wget "https://ca.nordugrid.org/${CERT_FILE}" -O "${CERT_FILE}"
sudo mv $CERT_FILE "/usr/local/share/ca-certificates/"
sudo chown root:root "/usr/local/share/ca-certificates/${CERT_FILE}"
sudo chmod 644 "/usr/local/share/ca-certificates/${CERT_FILE}"
sudo update-ca-certificates

arcproxy
voms-proxy-init
