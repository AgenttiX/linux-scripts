#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
. "${SCRIPT_DIR}/setup_common.sh"

echo "Configuring SSH."

chmod 700 "${SCRIPT_DIR}"
chmod 600 "${SCRIPT_DIR}/authorized_keys"
if [ -f "${SCRIPT_DIR}/config" ]; then
  chmod 600 "${SCRIPT_DIR}/config"
fi

if [ -L "${SSH_DIR}" ]; then
  echo "SSH folder is already a symlink. Skipping symlink creation."
else
  if [ -d "${SSH_DIR}" ]; then
    echo "Backing up old SSH folder."
    mv "${SSH_DIR}" "${SSH_DIR}-old"
  fi
  echo "Creating symlink to the SSH folder."
  ln -s "${CONF_DIR}" "${SSH_DIR}"
fi

echo "SSH configured."
