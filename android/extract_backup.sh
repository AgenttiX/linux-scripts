#!/usr/bin/env bash
set -eu

# ADB backup extractor
# Will not work on encrypted backups, but instead produces the error:
# "gzip: stdin: invalid compressed data--format violated"
# Arguments:
# - Source file (.ab)
# - Target folder
# - (Encryption password)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$(dirname "${SCRIPT_DIR}")"

if [ $# -eq 2 ]; then
  echo "No password was provided. Assuming that this is a non-encrypted backup."
elif [ $# -eq 3 ]; then
  echo "Password was provided. Using android-backup-extractor."
else
  echo "Invalid number of arguments."
  echo "Usage: extract_backup.sh <backup_path> <password>"
fi

if [[ "$1" != *".ab" ]]; then
  echo "The backup path should end with \".ab\"."
  exit 1
fi

if [ $# -eq 2 ]; then
  echo "Attempting direct extraction. This will fail if the backup is encrypted."
  # https://stackoverflow.com/a/46500482/
  # https://android.stackexchange.com/a/78183/
  if ( printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" ; tail -c +25 "$1" ) | tar xfvz - -C "$2"; then
    echo "Direct extraction succeeded."
    exit 0
  fi
  echo "Direct extraction failed. Falling back to android-backup-extractor."
fi

source "${REPO_DIR}/github.sh"
ABE="${SCRIPT_DIR}/abe.jar"
echo "Downloading android-backup-extractor."
download_latest_release "nelenkov/android-backup-extractor" "abe.jar" "${ABE}"
# BACKUP_PATH_WITHOUT_SUFFIX="${1%.ab}"
if [ $# -eq 2 ]; then
  echo "Unpacking with android-backup-extractor without password."
  java -jar "${ABE}" unpack "$1" "$2/backup.tar"
else
  echo "Unpacking with android-backup-extractor with password."
  java -jar "${ABE}" unpack "$1" "$2/backup.tar" "$3"
fi
