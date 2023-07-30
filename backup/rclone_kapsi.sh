#!/usr/bin/env bash
set -e

# Before running this script, run "rclone config" to configure rclone.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_PATH="${REPO_DIR}/logs/rsync_kapsi_${TIMESTAMP}.txt"

rclone sync \
  --progress \
  --exclude-from="${SCRIPT_DIR}/rsync_exclude.txt" \
  /mnt/files \
  kapsi-crypt:/files |& tee -a "${LOG_PATH}"
# --delete-excluded
