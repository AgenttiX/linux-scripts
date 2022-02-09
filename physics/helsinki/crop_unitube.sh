#!/usr/bin/sh -e
# This script crops the lecture hall camera from a Full HD Unitube video.
# https://video.stackexchange.com/questions/4563/how-can-i-crop-a-video-with-ffmpeg/4571#4571?newreg=d65c6681821c44358d04465f4a62793d
# https://trac.ffmpeg.org/wiki/Encode/H.264

if [ $# -ne 2 ]; then
  echo "Wrong number of parameters. Give paths for input and output files."
fi

# You can try these to speed up the encoding:
# "-preset ultrafast"
# "-hwaccel auto"
# If you have problems, you can remove the "-x264opts opencl"
ffmpeg -x264opts opencl -i "${1}" -filter:v "crop=480:270:1440:0" -c:a copy "${2}"
