#!/usr/bin/env bash
set -e

# Todo: This script has not been tested yet.

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

DISK=$1

apt-get update
apt-get install nvme-cli smartmontools

nvme list

# https://stackoverflow.com/a/1885534/
read -p "Are you sure this is the right disk? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

nvme format --ses=1 "${DISK}n1"

nvme device-self-test --self-test-code=2h "${DISK}"
nvme self-test-log "${DISK}"
smartctl --all "${DISK}"
