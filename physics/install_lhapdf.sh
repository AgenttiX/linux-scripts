#!/usr/bin/bash -e

# Installation script for LHAPDF
# https://lhapdf.hepforge.org/

if [ "$EUID" -eq 0 ]; then
  echo "This script should not be run as root."
  exit
fi

sudo apt-get install build-essential python3-dev wget
sudo pip3 install cython

LHAPDF_VERSION="6.3.0"
LHAPDF_FOLDER="LHAPDF-${LHAPDF_VERSION}"
LHAPDF_FILE="${LHAPDF_FOLDER}.tar.gz"

wget "https://lhapdf.hepforge.org/downloads/?f=${LHAPDF_FILE}" -O "${LHAPDF_FILE}"
tar xf $LHAPDF_FILE
cd $LHAPDF_FOLDER

# If Python 2 is installed as the default Python
if [[ $(python --version 2>&1) =~ [^2\.*] ]]; then
  echo "Python 2 detected. Installing Python 2 support separately."
  ./configure
  make -j"$(nproc)"
  sudo make install

  # Enable Python 3 support
  echo "Now enabling Python 3 support and installing again."
  export PYTHON="/usr/bin/python3"
fi

./configure
make -j"$(nproc)"
sudo make install

echo "LHAPDF has been installed. You can now safely remove the build folder."
