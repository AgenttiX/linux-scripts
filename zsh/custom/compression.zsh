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

unzip_recurse() {
  local FLAT=0
  local FOLDER=""
  local ARG
  for ARG in "$@"; do
    case "${ARG}" in
      -f|--flat)
        FLAT=1
        ;;
      *)
        FOLDER="${ARG}"
        ;;
    esac
  done

  if [ -z "${FOLDER}" ]; then
    echo "Please give the folder path."
    echo "Usage: unzip_recurse [-f|--flat] <folder>"
    return 1
  fi
  if [ ! -d "${FOLDER}" ]; then
    echo "Folder not found: ${FOLDER}"
    return 1
  fi
  local ARCHIVE DIR FILENAME NAME OUTDIR
  find "${FOLDER}" -type f \( -iname '*.zip' -o -iname '*.7z' \) -print0 | while IFS= read -r -d '' ARCHIVE; do
    DIR="$(dirname -- "${ARCHIVE}")"
    if [ "${FLAT}" -eq 1 ]; then
      OUTDIR="${DIR}"
    else
      FILENAME="$(basename -- "${ARCHIVE}")"
      NAME="${FILENAME%.*}"
      OUTDIR="${DIR}/${NAME}"
      mkdir -p -- "${OUTDIR}"
    fi
    echo "Extracting \"${ARCHIVE}\" to \"${OUTDIR}\""
    # 7-Zip overwrite modes:
    # -aoa = Overwrite all existing files without prompting
    # -aos = Skip extracting existing files
    # -aot = Auto-rename extracted files and keep the existing ones
    # -aou = Auto-rename existing files and extract new files in their place
    7z x -aos -o"${OUTDIR}" -- "${ARCHIVE}"
  done
}
