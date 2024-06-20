#!/usr/bin/env bash
set -eu

# yt-dlp is a better maintained and more feature-complete variant of the popular youtube-dl.
# https://github.com/yt-dlp/yt-dlp

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

sudo apt-get install \
  ffmpeg \
  mpv \
  python3-keyring \
  python3-mutagen \
  python3-websockets \
  rtmpdump
# Not needed: atomicparsley

python3 -m pip install --upgrade yt-dlp pycryptodomex
