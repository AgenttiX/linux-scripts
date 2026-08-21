#!/usr/bin/env zsh

compress_7z() {
  if [ $# -lt 1 ]; then
    echo "Please give the file path."
    return 1
  fi
  # https://stackoverflow.com/a/965072/
  local FILENAME=$(basename -- "$1")
  local NAME="${FILENAME%.*}"
  # https://superuser.com/a/742034/
  7zr a -t7z -mx=9 "${NAME}.7z" "${FILENAME}"
  7zr t "${NAME}.7z"
  echo "Computing SHA-256 checksum."
  sha256sum "${NAME}.7z" > "${NAME}.7z.sha256"
}

compress_zip() {
  if [ $# -lt 1 ]; then
    echo "Please give the file path."
    return 1
  fi
  # https://stackoverflow.com/a/965072/
  local FILENAME="$(basename -- "$1")"
  local NAME="${FILENAME%.*}"
  # https://superuser.com/a/742034/
  7z a -mm=Deflate -mfb=258 -mpass=15 "${NAME}.zip" "${FILENAME}"
  7z t "${NAME}.zip"
  echo "Computing SHA-256 checksum."
  sha256sum "${NAME}.zip" > "${NAME}.zip.sha256"
}
