#!/usr/bin/sh -e
# Ethereum mining script

# The configuration should be specified as variables in ethminer_config.sh
. ./ethminer_config.sh

ETHMINER="./ethminer/ethminer"
"$ETHMINER" --list-devices
# Restart ethminer if it dies
# https://stackoverflow.com/a/697064/
while true; do
  "$ETHMINER" -P "${SCHEME}://${ADDRESS}@${SERVER}:${PORT}"
  echo "Ethminer shut down. Restarting."
  sleep 30
done
