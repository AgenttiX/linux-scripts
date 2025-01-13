#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONF_DIR="/usr/lib/systemd/system-sleep"

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

if ! [ -d "${CONF_DIR}" ]; then
  echo "Config directory \"${CONF_DIR}\" was not found."
fi

echo "Enabling agx-suspend script."
cp "${SCRIPT_DIR}/agx-suspend-enabler.sh" "${CONF_DIR}"
chmod 755 "${CONF_DIR}/agx-suspend-enabler.sh"
echo "agx-suspend script enabled."
