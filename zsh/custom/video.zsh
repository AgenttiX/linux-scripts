#!/usr/bin/env zsh

trim_video() {
  if [ $# -ne 4 ]; then
    echo "Usage: trim_video <source path> <start time> <end time> <output path>"
    return 1
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

monitorconf() {
  local PRIMARY="DP-1"
  local VG248="DP-2"
  local VE247="DP-3"
  local TV="HDMI-A-1"
  case "${1}" in
    pc | PC)
      kscreen-doctor "output.${PRIMARY}.enable" "output.${VG248}.enable" "output.${VE247}.enable" "output.${TV}.disable" \
        "output.${PRIMARY}.mode.3440x1440@144" "output.${VG248}.mode.1920x1080@144" "output.${VE247}.mode.1920x1080@60" \
        "output.${VG248}.position.0,180" "output.${PRIMARY}.position.1920,0" "output.${VE247}.position.5360,180" \
        "output.${PRIMARY}.hdr.enable"
      ;;
    tv | TV)
      kscreen-doctor "output.${PRIMARY}.disable" "output.${VG248}.disable" "output.${VE247}.enable" "output.${TV}.enable" \
        "output.${VE247}.mode.1920x1080@60" "output.${TV}.mode.3840x2160@120" \
        "output.${VE247}.position.0,0" "output.${TV}.position.0,0" \
        "output.${TV}.wcg.enable" "output.${TV}.scale.2"
      ;;
  esac
}

yt-dlp-playlist() {
    if [ $# -ne 1 ]; then
    echo "Usage: yt-dlp-playlist <playlist url>"
  fi
  TITLE="$(yt-dlp --skip-download --print playlist_title --no-warnings "${1}" -I "1:1")"
  echo "Downloading playlist data: ${TITLE}"
  echo "Downloading data as txt:"
  yt-dlp -s --flat-playlist --print-to-file "%(url)s # %(title)s" "%(playlist_title)s.txt" "${1}"
  echo "Downloading data as json:"
  yt-dlp --dump-single-json --skip-download --no-warnings "${1}" > "${TITLE}.json"
  echo "Playlist data downloaded."
}
