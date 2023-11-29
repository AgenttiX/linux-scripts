#!/usr/bin/env bash
set -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "${LOG_DIR}"

# https://help.ubuntu.com/community/HirsuteUpgrades/Kubuntu
# If the upgrade fails, it's good to have a log file of the console output to see how things went wrong.
pkexec do-release-upgrade -m desktop -f DistUpgradeViewKDE |& tee "${LOG_DIR}/kubuntu_release_upgrade_$(date +%F_%H-%M-%S).txt"

# If Python has been updated, you can find and remove old virtualenvs with
# ls ${HOME}/Git/**/venv
# rm -r ${HOME}/Git/**/venv
