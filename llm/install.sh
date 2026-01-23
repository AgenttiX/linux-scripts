#!/usr/bin/env sh

# Nix is required for llama.cpp
if ! command -v nix &> /dev/null; then
    echo "Installing Nix."
    sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon
fi

if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama."
    curl -fsSL https://ollama.com/install.sh | sh
fi

nix profile install nixpkgs#llama-cpp --extra-experimental-features nix-command --extra-experimental-features flakes

which llama-server
llama-server --version

which llama-cli
llama-cli -hf Qwen/Qwen2.5-7B-Instruct-GGUF

llama-bench --list-devices
llama-bench --model ${HOME}/.cache/llama.cpp/Qwen_Qwen2.5-7B-Instruct-GGUF_qwen2.5-7b-instruct-q2_k.gguf
