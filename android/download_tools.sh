#!/usr/bin/sh -e

FILENAME="platform-tools-latest-linux.zip"
URL="https://dl.google.com/android/repository/${FILENAME}"

wget $URL -O $FILENAME
unzip $FILENAME
