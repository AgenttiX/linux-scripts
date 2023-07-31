#!/usr/bin/env bash
set -e

# Before running this script, run "rclone config" to configure rclone.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_PATH="${REPO_DIR}/logs/rclone_kapsi_${TIMESTAMP}.txt"

# Warning: the --delete-excluded flag will delete files on the target that are not part of the backup.
# First run the backup without --delete-excluded to see that it goes to the correct empty folder,
# and doesn't mess with other files on the target machine!
rclone sync \
  --progress \
  --exclude-from="${SCRIPT_DIR}/rsync_exclude.txt" \
  --delete-excluded \
  /mnt/files \
  kapsi-crypt:/files |& tee -a "${LOG_PATH}"
