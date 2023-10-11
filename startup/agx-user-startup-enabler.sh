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
  ln -sf "${SCRIPT_DIR}/agx-user-pre-startup.sh" "${PLASMA_WORKSPACE_DIR}/env/agx-user-pre-startup.sh"

  echo "Installing the agx-user-shutdown script."
  mkdir -p "${PLASMA_WORKSPACE_DIR}/shutdown"
  ln -sf "${SCRIPT_DIR}/agx-user-shutdown.sh" "${PLASMA_WORKSPACE_DIR}/shutdown/agx-user-shutdown.sh"
else
  echo "Plasma workspace config directory was not found. Cannot install pre-startup script."
fi

STARTUP_DIR="${HOME}/.config/autostart/"
if [ -d "${STARTUP_DIR}" ]; then
  echo "Installing the agx-user-startup script."
  DESKTOP_FILE="${STARTUP_DIR}/agx-user-startup.desktop"
  cp "${SCRIPT_DIR}/agx-user-startup.desktop" "${DESKTOP_FILE}"
  # The .desktop files don't support ~ or $HOME
  sed -i "s@SCRIPT_DIR@${SCRIPT_DIR}@g" "${DESKTOP_FILE}"
else
  echo "Autostart directory was not found. Cannot install startup script."
fi

echo "Installation ready."
