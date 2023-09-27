#!/usr/bin/env sh
# From https://github.com/xaberus/vscode-remote-oss

export CONNECTION_TOKEN=wGyLXg0Z6NTbsTMd
export REMOTE_PORT=11111

~/.vscodium-server/bin/current/bin/codium-server \
    --host localhost \
    --port ${REMOTE_PORT} \
    --telemetry-level off \
    --connection-token ${CONNECTION_TOKEN}
