#!/usr/bin/bash -e

# Installation script for Pythia8
# http://home.thep.lu.se/~torbjorn/Pythia.html

if [ "$EUID" -eq 0 ]; then
  echo "This script should not be run as root."
  exit
fi

if ! [ -f "/usr/local/bin/lhapdf" ]; then
  echo "LHAPDF is not installed. Please install it first."
  exit
fi

sudo apt-get install python3-dev

PYTHIA_VERSION="8303"
PYTHIA_FOLDER="pythia${PYTHIA_VERSION}"
PYTHIA_FILE="${PYTHIA_FOLDER}.tgz"
PYTHIA_URL="http://home.thep.lu.se/~torbjorn/pythia8/${PYTHIA_FILE}"

wget $PYTHIA_URL -O $PYTHIA_FILE
tar xvfz $PYTHIA_FILE
cd $PYTHIA_FOLDER

# Todo: fix the generation of Python bindings.
# At the moment they are not generated for some reason.
# alias python="/usr/bin/python3"
# --with-python-bin=/usr/bin
./configure --prefix=/usr/local --with-gzip --with-openmp --with-python --with-python-config=python3-config --with-lhapdf6
make -j"$(nproc)"
sudo make install
