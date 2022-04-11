#!/usr/bin/bash -e
# Installation script for OCRmyPDF
# https://ocrmypdf.readthedocs.io/en/latest/

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

sudo apt update
sudo apt install libleptonica-dev libtool ocrmypdf

mkdir -p "${HOME}/Git"
if [ -d "${HOME}/Git/jbig2enc" ]; then
  echo "jbig2enc seems to be already downloaded. Updating the repository."
  cd "${HOME}/Git/jbig2enc"
  git pull
else
  echo "jbig2enc seems not to be downloaded yet. Cloning the repository."
  cd "${HOME}/Git"
  git clone "https://github.com/agl/jbig2enc"
  cd "${HOME}/Git/jbig2enc"
fi
echo "Installing jbig2enc"
./autogen.sh
./configure
make
sudo make install
