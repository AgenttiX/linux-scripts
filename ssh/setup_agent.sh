#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
. "${SCRIPT_DIR}/setup_common.sh"

CONF_SCRIPT="${CONF_DIR}/setup_agent.sh"

if [ ! -f "${CONF_SCRIPT}" ]; then
  echo "The agent configuration was not found at: ${CONF_SCRIPT}"
  exit 1
fi

echo "Configuring SSH agent."

# Wait for kwallet
if command -v kwallet-query &> /dev/null; then
  # If you get exit code 4 here, create a folder named "Passwords" manually in KDE Wallet.
  kwallet-query -l kdewallet > /dev/null
fi

echo "Removing existing identities."
ssh-add -D

echo "Adding new identities."
# Warning! All added keys that are used for multiple devices
# must be on FIDO2 security keys and require physical confirmation.
# Otherwise the server you connect to can use the SSH keys
# as if it was your local machine!

# Support for TPM-based keys
# The path changed with Kubuntu 25.04.
LIBTPM2_PKCS11="/usr/lib/x86_64-linux-gnu/pkcs11/libtpm2_pkcs11.so"
LIBTPM2_PKCS11_OLD="/usr/lib/x86_64-linux-gnu/libtpm2_pkcs11.so.1"
if [ -f "${LIBTPM2_PKCS11}" ]; then
  set +e
  ssh-add -s "${LIBTPM2_PKCS11}"
  set -e
elif [ -f "${LIBTPM2_PKCS11_OLD}" ]; then
  set +e
  ssh-add -s "${LIBTPM2_PKCS11_OLD}"
  set -e
fi

# The id_rsa is only used for specific purposes
if [ -f "${HOME}/.ssh/id_rsa" ]; then
  ssh-add "${HOME}/.ssh/id_rsa"
fi

# Support for smart cards. These may require a PIN, which is why this is after id_rsa.
# https://www.linux.fi/wiki/HST#Ssh_2
OPENSC_PKCS11="/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so"
if [ -f "${OPENSC_PKCS11}" ]; then
  set +e
  ssh-add -s "${OPENSC_PKCS11}"
  set -e
fi

. "${CONF_SCRIPT}"

echo "Configured identities:"
ssh-add -L
