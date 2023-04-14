#!/usr/bin/env bash
set -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

PLASMA_WORKSPACE_DIR="${HOME}/.config/plasma-workspace"
if [ -d "${PLASMA_WORKSPACE_DIR}" ]; then
  echo "Installing the agx-user-pre-startup script."
  mkdir -p "${PLASMA_WORKSPACE_DIR}/env"
  ln -s "${SCRIPT_DIR}/agx-user-pre-startup.sh" "${PLASMA_WORKSPACE_DIR}/env/agx-user-pre-startup.sh"
else
  echo "Plasma workspace config directory was not found. Cannot install pre-startup script."
fi

STARTUP_DIR="${HOME}/.config/autostart/"
if [ -d "${STARTUP_DIR}" ]; then
  echo "Installing the agx-user-startup script."
  ln -s "${SCRIPT_DIR}/agx-user-startup.desktop" "${STARTUP_DIR}/agx-user-startup.desktop"
else
  echo "Autostart directory was not found. Cannot install startup script."
fi

echo "Installation ready."