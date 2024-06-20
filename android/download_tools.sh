#!/usr/bin/env sh
set -eu

FILENAME="platform-tools-latest-linux.zip"
URL="https://dl.google.com/android/repository/${FILENAME}"

rm -f $FILENAME
wget $URL -O $FILENAME
rm -rf ./platform-tools
unzip $FILENAME
