#!/bin/bash -e
# Configuration script for working on University of Helsinki workstations

# SSH setup
if ! [ -d "${HOME}/.ssh" ]; then
  echo "Creating SSH symlink."
  ln -s "/home/ad/home/${USER:0:1}/${USER}/.ssh" "${HOME}/.ssh"
fi

# Git setup
if ! [ -d "${HOME}/Git" ]; then
  echo "Creating Git directory."
  mkdir "${HOME}/Git"
fi

# Script repo setup
REPO_DIR="${HOME}/Git/linux-scripts"
if ! [ -d "${REPO_DIR}" ]; then
  if [ -f "${HOME}/.ssh/id_rsa" ]; then
    git clone "git@github.com:AgenttiX/linux-scripts.git"
    python3 -m venv "${REPO_DIR}/venv"
    source "${REPO_DIR}/venv/bin/activate"
    pip3 install -r "${REPO_DIR}/requirements.txt"
  else
    echo "SSH key does not exist. Cannot clone linux-scripts repo."
    exit 1
  fi
fi

# Notes network drive
KAPSI_USER="agenttix"
LOCAL_DIR="/tmp/${USER}"
NOTES_DIR="${LOCAL_DIR}/Mount/HY"
if ! [ -d "${LOCAL_DIR}" ]; then
  echo "Creating local directory for mounts."
  mkdir -p "${LOCAL_DIR}"
  chmod 700 "${LOCAL_DIR}"
fi
if ! [ -d "${NOTES_DIR}" ]; then
  echo "Creating notes directory."
  mkdir -p "${NOTES_DIR}"
  chmod 700 "${NOTES_DIR}"
fi
if ! [ -d "${HOME}/HY" ]; then
  echo "Creating symlink for the notes directory."
  ln -s "${NOTES_DIR}" "${HOME}/HY"
fi
if mountpoint -q "${NOTES_DIR}"; then
  echo "Notes directory is already mounted."
else
  echo "Mounting notes directory."
  chmod 700 "${NOTES_DIR}"
  sshfs "${KAPSI_USER}@kapsi.fi:/home/users/${KAPSI_USER}/siilo/syncthing/hy/" "${NOTES_DIR}"
fi

# Xournal++
XOURNALPP_DIR="${HOME}/.xournalpp"
if ! [ -L "${XOURNALPP_DIR}" ]; then
  if [ -d "${XOURNALPP_DIR}" ]; then
    echo "Removing old non-synced Xournal++ config directory."
    rm -r "${XOURNALPP_DIR}"
  fi
  ln -s "${REPO_DIR}/xournalpp" "${XOURNALPP_DIR}"
fi

# System settings
if ! command -v gsettings &> /dev/null; then
  # https://unix.stackexchange.com/a/37545
  gsettings set org.gnome.desktop.wm.preferences resize-with-right-button true
  # https://unix.stackexchange.com/a/459815
  gsettings set org.gnome.desktop.peripherals.mouse accel-profile flat
fi

# Wacom tablet
# The script fail if a tablet is not connected, so it's the last.
source "${REPO_DIR}/venv/bin/activate"
echo "Configuring Wacom tablet."
"${REPO_DIR}/wacom/wacom.py"
