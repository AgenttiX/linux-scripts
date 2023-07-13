#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_PATH="${REPO_DIR}/logs/rsync_backup_${TIMESTAMP}.txt"

rsync \
  --archive --compress --delete --partial --progress --stats \
  --exclude-from="${SCRIPT_DIR}/rsync_exclude.txt" \
  "/home" \
  "${USER}@agx-file-backup:." |& tee -a "${LOG_PATH}"
