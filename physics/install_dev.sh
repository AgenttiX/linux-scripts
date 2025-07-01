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
# libedit-dev seems to be required for cmake compilation of AdaptiveCPP
apt install build-essential clang cmake hdf5-tools hipcc \
  libboost-dev libboost-context-dev libboost-fiber-dev libboost-test-dev \
  libedit-dev libgomp1 libhdf5-mpi-dev libomp-dev lld mpi-default-dev ninja-build pkg-config

snap install clion --classic
snap install rustrover --classic
