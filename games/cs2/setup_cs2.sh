#!/usr/bin/env bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

CS2_SCRIPT_PATH="/home/mika/.steam/steam/steamapps/common/Counter-Strike Global Offensive/game/cs2.sh"
if [ -f "${CS2_SCRIPT_PATH}" ] && [ ! -L "${CS2_SCRIPT_PATH}" ]; then
  echo "Backing up original cs2.sh"
  mv "${CS2_SCRIPT_PATH}" "${CS2_SCRIPT_PATH}.bak"
fi
echo "Creating symlink to cs2.sh"
ln -s "${SCRIPT_DIR}/cs2.sh" "${CS2_SCRIPT_PATH}"
