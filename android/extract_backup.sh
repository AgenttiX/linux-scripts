#!/usr/bin/bash -e

# ADB backup extractor
# Will not work on encrypted backups, but instead produces the error:
# "gzip: stdin: invalid compressed data--format violated"

if [ $# -eq 1 ]; then
  echo "No password was provided. Assuming that this is a non-encrypted backup."
elif [ $# -eq 2 ]; then
  echo "Password was provided. Using android-backup-extractor."
else
  echo "Invalid number of arguments."
  echo "Usage: extract_backup.sh <backup_path> <password>"
fi

if [[ $1 != *".ab" ]]; then
  echo "The backup path should end with \".ab\"."
  exit 1
fi

if [ $# -eq 1 ]; then
  echo "Attempting direct extraction. This will fail if the backup is encrypted."
  # https://stackoverflow.com/a/46500482/
  # https://android.stackexchange.com/a/78183/
  if ( printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" ; tail -c +25 "$1" ) | tar xfvz -; then
    echo "Direct extraction succeeded."
    exit 0
  fi
  echo "Direct extraction failed. Falling back to android-backup-extractor."
fi

source ../github.sh
ABE="./abe.jar"
download_latest_release "nelenkov/android-backup-extractor" "abe.jar" $ABE
BACKUP_PATH_WITHOUT_SUFFIX="${1%.ab}"
if [ $# -eq 1 ]; then
  java -jar $ABE unpack "$1" "${BACKUP_PATH_WITHOUT_SUFFIX}.tar"
else
  java -jar $ABE unpack "$1" "${BACKUP_PATH_WITHOUT_SUFFIX}.tar" "$2"
fi
