#!/usr/bin/sh -e
# Ethereum mining script

# The configuration should be specified as variables in ethminer_config.sh
. ./ethminer_config.sh

ETHMINER="./ethminer/ethminer"
"$ETHMINER" --list-devices
"$ETHMINER" -P "${SCHEME}://${ADDRESS}@${SERVER}:${PORT}"
