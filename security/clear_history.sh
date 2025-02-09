#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"

# Bash history
# Handled by BleachBit
# history -c

python3 "${REPO_DIR}/maintenance.py" --bleachbit-only

# https://askubuntu.com/a/155777/
# https://www.tecmint.com/clear-ram-memory-cache-buffer-and-swap-space-on-linux/
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

# TODO: Add BleachBit here

# TRIM free disk space
fstrim -a -v
