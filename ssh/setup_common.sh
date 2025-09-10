#!/usr/bin/env bash
set -eu

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "Please give the name of the repo containing the config files."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SSH_DIR="${HOME}/.ssh"
# Location of the SSH configuration directory in the other repo
CONF_DIR="$(dirname "$(dirname "${SCRIPT_DIR}")")/$1/ssh"

if [ ! -d "${CONF_DIR}" ]; then
  echo "Config directory was not found: ${CONF_DIR}"
  exit 1
fi
