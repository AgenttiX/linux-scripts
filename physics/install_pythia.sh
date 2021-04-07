#!/usr/bin/bash -e

# Installation script for Pythia8
# http://home.thep.lu.se/~torbjorn/Pythia.html

# For the Python bindings to work, one of the following additional steps is needed.
# a) Add Pythia library folder /usr/local/lib to $PYTHONPATH in .zshrc or a similar global config file
# b) Add Pythia library folder to $PATH or $PYTHONPATH dynamically as in /usr/local/share/Pythia8/examples/main01.py

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

./configure \
  --prefix=/usr/local \
  --with-gzip \
  --with-lhapdf6 \
  --with-openmp \
  --with-python \
  --with-python-config=python3-config \
  --with-python-include="$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")" \
  --with-python-lib="$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")"
  # --with-python-bin=/usr/bin
make -j"$(nproc)"
sudo make install
