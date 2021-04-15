#!/usr/bin/bash -e

# Installation script for Geant4
# https://geant4.web.cern.ch/

if [ "$EUID" -eq 0 ]; then
  echo "This script should not be run as root."
  exit
fi

sudo apt-get install \
  build-essential \
  cmake \
  cython3 \
  libboost-dev \
  libboost-python-dev \
  libhdf5-dev \
  libmotif-dev \
  libxerces-c-dev \
  libxmu-dev \
  python3-dev \
  python3-pip \
  wget
sudo pip3 install scikit-build
# Timemory requires that scikit-build is already installed
sudo pip3 install timemory

GEANT_VERSION="4.10.07.p01"
GEANT_FOLDER="geant${GEANT_VERSION}"
GEANT_FILE="${GEANT_FOLDER}.tar.gz"

if ! [ -f "$GEANT_FILE" ]; then
  wget "http://cern.ch/geant4-data/releases/${GEANT_FILE}" -O $GEANT_FILE
else
  echo "Using already downloaded sources."
fi
rm -rf $GEANT_FOLDER
tar xf $GEANT_FILE
cd $GEANT_FOLDER
mkdir -p build
cd build

cmake .. \
  -DGEANT4_BUILD_MULTITHREADED=ON \
  -DGEANT4_BUILD_TLS_MODEL=global-dynamic \
  -DGEANT4_INSTALL_DATA=ON \
  -DGEANT4_USE_FREETYPE=ON \
  -DGEANT4_USE_G3TOG4=ON \
  -DGEANT4_USE_GDML=ON \
  -DGEANT4_USE_HDF5=ON \
  -DGEANT4_USE_OPENGL_X11=ON \
  -DGEANT4_USE_PYTHON=ON \
  -DGEANT4_USE_QT=ON \
  -DGEANT4_USE_RAYTRACER_X11=ON \
  -DGEANT4_USE_XM=ON
  # -DGEANT4_USE_INVENTOR=ON \
  # -DGEANT4_USE_INVENTOR_QT=ON \
  # -DGEANT4_USE_TBB=ON \
  # This requires Timemory 3.2, but the latest version on PyPi is 3.1 as of 2021-04-15
  # -DGEANT4_USE_TIMEMORY=ON \
make -j"$(nproc)"
sudo make install

PYTHON3_VERSION_STR=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
sudo ln -s "/usr/local/lib/python${PYTHON3_VERSION_STR}/site-packages/Geant4" "/usr/local/lib/python${PYTHON3_VERSION_STR}/dist-packages/Geant4"

echo "Geant has been installed. You can now safely remove the build folder."
