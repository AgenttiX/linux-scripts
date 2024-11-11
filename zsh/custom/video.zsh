#!/usr/bin/env zsh

trim_video() {
  if [ $# -ne 4 ]; then
    echo "Usage: trim_video <source path> <start time> <end time> <output path>"
    exit 1
  fi
  ffmpeg -i $1 -ss $2 -to $3 -c:v copy -c:a copy $4
}

fix_rotation() {
  # Fix wrong rotation metadata in a video.
  # Custom Android ROMs can sometimes give wrong orientation sensor data,
  # resulting in wrong orientation metadata in video recordings.
  if [ $# -lt 1 ]; then
    echo "Usage: fix_rotation <source paths>"
  fi
  for ARG in "$@"; do
    NAME="${ARG%.*}"
    SUFFIX="${ARG##*.}"
    OLD_NAME="${NAME}-old.${SUFFIX}"
    mv "${ARG}" "${OLD_NAME}"
    ffmpeg -display_rotation 0 -i "${OLD_NAME}" -c copy "${ARG}"
  done
}
