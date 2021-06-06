#!/usr/bin/bash -e
# Backup an Android device with ADB

if [ $# -ne 1 ]; then
  echo "Please give the backup path as argument. Use the .ab file extension."
  exit 1
fi
if [[ $1 != *".ab" ]]; then
  echo "The backup path should end with \".ab\"."
  exit 1
fi

# https://stackoverflow.com/a/246128/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ADB="$SCRIPT_DIR/platform-tools/adb"

# -all = backup all installed applications
# -apk = backup apk files
# -f = set file path
# -obb = backup apk expansion (.obb) files
# -shared = backup shared storage / SD card
# -system = -all should also backup system applications
$ADB backup -all -apk -obb -shared -system -f "$1"

echo "Backup ready. Don't forget to check that it actually contains all your data!"
