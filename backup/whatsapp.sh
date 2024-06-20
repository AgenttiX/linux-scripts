#!/usr/bin/env bash
set -eu

# WORK IN PROGRESS

copy_wa() {
  local FILES="${1}/*-${YEAR}*.mp4"
  local FILES_SENT="${1}/Sent/*-${YEAR}*.*"
  if compgen -G "${FILES}" > /dev/null; then
    local TARGET="${2}/${YEAR}"
    echo "Moving: \"${FILES}\" -> \"${TARGET}\""
    mkdir -p "${TARGET}"
    # https://stackoverflow.com/a/54635203/
    # find . -wholename "${FILES}" -exec mv '{}' "${TARGET}/" \;
    rsync -avh --progress --remove-source-files "${FILES}" "${TARGET}/"
  else
    echo "No files found: \"${FILES}\""
  fi
  if compgen -G "${FILES_SENT}" > /dev/null; then
    echo "Moving: \"${FILES_SENT}\" -> \"${TARGET_SENT}\""
    local TARGET_SENT="${2}/${YEAR}/Sent"
    mkdir -p "${TARGET_SENT}"
    # find . -wholename "${FILES_SENT}" -exec mv '{}' "${TARGET_SENT}/" \;
    rsync -avh --progress --remove-source-files "${FILES}" "${TARGET}/"
  else
    echo "No files found: \"${FILES_SENT}\""
  fi
}

SOURCE_DIR="/mnt/serveriraid/Syncthing/WhatsApp"
MEDIA_DIR="${SOURCE_DIR}/Media"
ARCHIVE_DIR="/mnt/serveriraid/Arkisto/WhatsApp"
BACKUP_DIR="/mnt/serveriraid/Varmuuskopiot/WhatsApp"

FOLDERS=(
  "Animated Gifs"
  "Images"
  "Video"
)

# cp -r "${SOURCE_DIR}/Backups" "${BACKUP_DIR}"
# cp -r "${SOURCE_DIR}/Databases" "${BACKUP_DIR}"

for YEAR in 2021 2022 2023; do
  echo "Processing year ${YEAR}"
  for FOLDER in "${FOLDERS[@]}"; do
    copy_wa "${MEDIA_DIR}/WhatsApp ${FOLDER}" "${ARCHIVE_DIR}/${FOLDER}"
  done
done
