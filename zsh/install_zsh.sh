#!/usr/bin/env bash
set -eu

if [ "${EUID}" -eq 0 ]; then
   echo "This script should not be run as root."
   exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Installing zsh and plugin dependencies."
sudo apt-get update
sudo apt-get install autojump build-essential cmake git ruby-dev zsh
gem install colorls

echo "Creating symlinks."
ln -s "${SCRIPT_DIR}/.zshenv" "${HOME}/.zshenv"
ln -s "${SCRIPT_DIR}/.p10k.zsh" "${HOME}/.p10k.zsh"

echo "zsh installed."
