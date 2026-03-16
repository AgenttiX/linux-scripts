#!/usr/bin/env bash
set -eu

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Nix is required for llama.cpp
if ! command -v nix &> /dev/null; then
  echo "Installing Nix."
  sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon
  echo "Please close and reopen your shell, and then rerun this script."
  return 1
fi

if ! command -v ollama &> /dev/null; then
  echo "Installing Ollama."
  curl -fsSL https://ollama.com/install.sh | sh
fi

if ! command -v llama-server &> /dev/null; then
  echo "Installing llama.cpp."
  nix profile install nixpkgs#llama-cpp --extra-experimental-features nix-command --extra-experimental-features flakes
fi

# if [ ! -f "${SCRIPT_DIR}/LM-Studio-"* ]; then
#   echo "Downloading LM Studio."
#   # This does not pick up the filename properly.
#   curl -JLO "https://lmstudio.ai/download/latest/linux/x64" --output-dir "${SCRIPT_DIR}"
#   chmod +x "${SCRIPT_DIR}/LM-Studio-"*
# fi

echo "Creating LM Studio shortcut symlink."
ln -f -s "${SCRIPT_DIR}/lm-studio.desktop" "${HOME}/.local/share/applications/lm-studio.desktop"

ollama --version

which llama-server
llama-server --version

which llama-cli
# llama-cli -hf Qwen/Qwen2.5-7B-Instruct-GGUF

llama-bench --list-devices
# llama-bench --model ${HOME}/.cache/llama.cpp/Qwen_Qwen2.5-7B-Instruct-GGUF_qwen2.5-7b-instruct-q2_k.gguf
