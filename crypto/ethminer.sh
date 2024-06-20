#!/usr/bin/env sh
set -eu

# Ethereum mining script

# The configuration should be specified as variables in ethminer_config.sh
. ./ethminer_config.sh

ETHMINER="./ethminer/ethminer"
"$ETHMINER" --list-devices
# Restart ethminer if it dies
# https://stackoverflow.com/a/697064/
while true; do
  if [ "$(hostname)" = "agx-z2e-kubuntu" ]; then
    # Disable the old secondary GPU on my desktop, as it's no longer profitable.
    echo "Starting Ethminer with only the primary GPU"
    "$ETHMINER" -P "${SCHEME}://${ADDRESS}@${SERVER}:${PORT}" --opencl --cl-devices 0
  else
    echo "Starting Ethminer"
    "$ETHMINER" -P "${SCHEME}://${ADDRESS}@${SERVER}:${PORT}"
  fi
  echo "Ethminer shut down. Restarting."
  sleep 30
done
