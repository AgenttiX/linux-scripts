#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_PATH="${REPO_DIR}/logs/rsync_backup_${TIMESTAMP}.txt"
HOSTNAME="$(hostname)"
HOSTNAME_TRIMMED="${HOSTNAME%"-kubuntu"}"

if [ "$#" -ne 1 ]; then
  echo "Usage: ${0} <home|root>"
  exit 1
elif [ "${1}" == "home" ]; then
  rsync \
    --archive --compress --delete --partial --progress --stats \
    --exclude-from="${SCRIPT_DIR}/rsync_exclude_home.txt" \
    "${HOME}" \
    "${USER}@agx-file-backup:/mnt/backup/${HOSTNAME_TRIMMED}/rsync/" |& tee -a "${LOG_PATH}"
elif [ "${1}" == "root" ]; then
  rsync \
    --archive --delete --partial --progress --stats \
    --exclude-from="${SCRIPT_DIR}/rsync_exclude_root.txt" \
    / \
    "/mnt/h12-backup-3tb/rsync/" |& tee -a "${LOG_PATH}"
else
  echo "Usage: ${0} <home|root>"
  exit 1
fi
