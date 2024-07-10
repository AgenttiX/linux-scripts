#!/usr/bin/env bash
set -eu

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

git pull
sudo "${SCRIPT_DIR}/maintenance_sudo.sh"
