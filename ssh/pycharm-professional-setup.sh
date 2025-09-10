#!/usr/bin/env bash
set -eu

# This was an experiment to fix the use of TPM SSH keys with PyCharm Professional.
# It turned out not to work, since PyCharm is using its own SSH implementation.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DESKTOP_PATH="${SCRIPT_DIR}/pycharm-professional.desktop"

echo "Validating the desktop file."
desktop-file-validate "${DESKTOP_PATH}"

echo "Creating symlink."
ln -f -s "${DESKTOP_PATH}" "${HOME}/.local/share/applications/pycharm-professional.desktop"
