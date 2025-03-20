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
  # Monitors:
  # DP-1 = VG248
  # DP-2 = 34GK950F
  # DP-3 = VE247
  # HDMI-A-1 = TV
  case "${1}" in
    pc | PC)
      kscreen-doctor output.DP-1.enable output.DP-2.enable output.DP-3.enable output.HDMI-A-1.disable \
        output.DP-1.mode.1920x1080@144 output.DP-2.mode.3440x1440@144 output.DP-3.mode.1920x1080@60 \
        output.DP-1.position.0,180 output.DP-2.position.1920,0 output.DP-3.position.5360,180
      ;;
    tv | TV)
      kscreen-doctor output.DP-1.disable output.DP-2.disable output.DP-3.enable output.HDMI-A-1.enable \
        output.DP-3.mode.1920x1080@60 output.HDMI-A-1.mode.3840x2160@120 \
        output.DP-3.position.0,0 output.HDMI-A-1.position.0,0 \
        output.HDMI-A-1.wcg.enable output.HDMI-A-1.scale.2
      ;;
  esac
}
