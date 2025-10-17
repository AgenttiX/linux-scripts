#!/usr/bin/env bash
set -eu

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

apt update
# Boost is required for AdaptiveCPP
# https://github.com/AdaptiveCpp/AdaptiveCpp
# These seem to be also required for its cmake compilation: libedit-dev, libclang-rt-dev
apt install build-essential clang clangd cmake hdf5-tools \
  libboost-dev libboost-context-dev libboost-fiber-dev libboost-test-dev \
  libclang-rt-dev libedit-dev libfftw3-dev libgomp1 libgsl-dev libhdf5-mpi-dev \
  libomp-dev lld mpi-default-dev ninja-build pkg-config \
  python3-dev python3-pylsp python3-pylsp-mypy python3-venv

# These should perhaps be added to the list above: hipcc

# Attempting to install multiple snaps simultaneously with classic containment results in this error:
# error: cannot specify mode for multiple store snaps (only for one store snap or several local ones)
snap install clion --classic
snap install rustrover --classic
