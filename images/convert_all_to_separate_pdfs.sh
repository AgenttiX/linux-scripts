#!/usr/bin/env sh
set -e

for FILE_PATH in "$1"/*.png; do
  # https://stackoverflow.com/a/965072/
  FILENAME="$(basename -- "$FILE_PATH")"
  NAME="${FILENAME%.*}"
  echo "${FILENAME} -> ${NAME}.pdf"
  convert "${FILENAME}" "${NAME}.pdf"
done
