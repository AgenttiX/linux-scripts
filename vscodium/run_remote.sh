#!/usr/bin/env bash
set -e

# From https://github.com/xaberus/vscode-remote-oss

if [ ! -f "${HOME}/.gitconfig" ]; then
    # shellcheck disable=SC2088
    echo "~/.gitconfig was not found. Please create it before running this script again."
    exit 1
fi
CONNECTION_TOKEN="$(sha256sum "${HOME}/.gitconfig" | cut -f 1 -d " ")"
export CONNECTION_TOKEN
export REMOTE_PORT=11111

~/.vscodium-server/bin/current/bin/codium-server \
    --host localhost \
    --port "${REMOTE_PORT}" \
    --telemetry-level off \
    --connection-token "${CONNECTION_TOKEN}"
