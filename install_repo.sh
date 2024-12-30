#!/usr/bin/env bash
set -eu

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

if command -v git &> /dev/null; then :; else
  echo "Git is not installed. Installing."
  sudo apt-get update
  sudo apt-get install git
fi

mkdir -p "${HOME}/Git"
cd "${HOME}/Git"
git clone "https://github.com/AgenttiX/linux-scripts.git"

echo "Script repo ready at ${HOME}/Git/linux-scripts"
