#!/usr/bin/env bash
set -euo pipefail

# Phoronix Test Suite documentation
# https://github.com/phoronix-test-suite/phoronix-test-suite/blob/master/documentation/phoronix-test-suite.md

SCRIPT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &> /dev/null && pwd )"
DIR="$(dirname "${SCRIPT_DIR}")/report/pts"
mkdir -p "${DIR}"

phoronix-test-suite system-info |& tee "${DIR}/system-info.txt"
phoronix-test-suite system-sensors |& tee "${DIR}/system-sensors.txt"
phoronix-test-suite diagnostics |& tee "${DIR}/system-sensors.txt"


phoronix-test-suite run \
  # CPU tests
  pts/av1 \
  pts/build-linux-kernel \
  pts/compress-7zip \
  pts/encode-flac \
  pts/ffmpeg \
  # RAM tests
  pts/ramspeed \
  pts/stream \
  # I/O tests
  pts/fio \
  # GPU tests
  pts/furmark \
  pts/mandelgpu \
  pts/mandelbulbgpu \
  system/clpeak \
  pts/vkpeak \
  # General tests
  pts/blender \
  # HPC tests
  pts/numpy \
  pts/pyhpc \
  pts/scikit-learn \
  # Machine learning
  pts/llama-cpp \
  pts/pytorch \
  pts/tensorflow \
  # Gaming tests
  pts/csgo \
  pts/openarena \
  pts/quake2rtx \
  pts/unigine \
  # pts/unigine-heaven \
  # pts/unigine-sanctuary \
  # pts/unigine-superposition \
  # pts/unigine-tropics \
  # pts/unigine-valley
  # These require a license
  # pts/geekbench
