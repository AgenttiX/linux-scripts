#!/usr/bin/bash -e
# Downloader for YouTube livestreams
# Based on:
# https://stackoverflow.com/a/37074870/

if [ "$1" == "" ]; then
  echo "Please give the url as an argument."
  exit 1;
fi
URL=$1

youtube-dl -F "${URL}"
read -p "Enter a format code from above: " FORMAT
STREAM_URL=$(youtube-dl -f "${FORMAT}" -g "${URL}")
ffmpeg -i "${STREAM_URL}" -c copy livestream.ts
