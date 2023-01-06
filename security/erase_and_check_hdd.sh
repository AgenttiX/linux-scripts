#!/bin/bash -e

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

DISK=$1
if ! [ -e "${DISK}" ]; then
  echo "Please supply a valid disk as the only argument."
  exit 1
fi

if ! (command -v smartctl &> /dev/null); then
  echo "smartmontools seems not to be installed. Installing."
  apt-get install smartmontools
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_DIR="$(dirname "${SCRIPT_DIR}")/logs"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "${LOG_DIR}"

smartctl --info "${DISK}"
hdparm -I "${DISK}" &> "${LOG_DIR}/hdparm_${TIMESTAMP}.txt"
# For some reason this status check does not seem to work yet.
if smartctl --all "${DISK}" &> "${LOG_DIR}/smartctl_${TIMESTAMP}_before.txt"; then
  read -p "This disk seems to have errors. Do you want to continue?" -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
      [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
  fi
fi

# https://stackoverflow.com/a/1885534/
read -p "Are you sure this is the right disk? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi

badblocks -wsv "${DISK}" -o "${LOG_DIR}/badblocks_${TIMESTAMP}.txt"
smartctl --test=long "${DISK}"
smartctl --all "${DISK}" |& tee "${LOG_DIR}/smartctl_${TIMESTAMP}_after.txt"
