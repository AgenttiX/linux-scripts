#!/usr/bin/env zsh

trim_video() {
  if [ $# -ne 4 ]; then
    echo "Usage: trim_video <source path> <start time> <end time> <output path>"
    exit 1
  fi
  ffmpeg -i $1 -ss $2 -to $3 -c:v copy -c:a copy $4
}
