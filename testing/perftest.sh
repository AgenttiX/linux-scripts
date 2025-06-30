#!/bin/bash -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

# This already runs apt-get update
source ./report.sh --no-report

# Function definitions

function run_geekbench_gpu() {
  VERSION=$1
  GEEKBENCH_SEARCH=( "${SCRIPT_DIR}/geekbench/Geekbench-${VERSION}."*"/geekbench_x86_64" )
  GEEKBENCH="${GEEKBENCH_SEARCH[0]}"
  OUTPUT="${DIR}/geekbench${VERSION}.txt"
  $GEEKBENCH --sysinfo |& tee "${DIR}/geekbench${VERSION}.txt"
  $GEEKBENCH --compute-list |& tee -a "${DIR}/geekbench${VERSION}.txt"
  $GEEKBENCH --cpu --save "${DIR}/geekbench${VERSION}_result_cpu.txt" |& tee -a "${OUTPUT}"

  # TODO: process --compute-list and run on all GPUs
  $GEEKBENCH --compute CUDA --save "${DIR}/geekbench${VERSION}_result_cuda.txt" |& tee -a "${OUTPUT}"
  $GEEKBENCH --compute OpenCL --save "${DIR}/geekbench${VERSION}_result_opencl.txt"|& tee -a "${OUTPUT}"
}

# Installers

if ! which speedtest > /dev/null; then
  curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
fi
sudo apt-get install sysbench speedtest stress-ng wget

./geekbench/download_geekbench.sh

if ! which phoronix-test-suite > /dev/null; then
  FILENAME="phoronix-test-suite_10.8.4_all.deb"
  wget "https://phoronix-test-suite.com/releases/repo/pts.debian/files/${FILENAME}" -O "${FILENAME}"
  sudo dpkg -i "${FILENAME}"
  rm "${FILENAME}"
  phoronix-test-suite openbenchmarking-login
  phoronix-test-suite batch-setup
fi
phoronix-test-suite openbenchmarking-refresh

# Tests

speedtest |& tee "${DIR}/speedtest.txt"

# These are managed by PTS
# 7z b -mmt1 |& tee "${DIR}/7z_single_thread.txt"
# 7z b |& tee "${DIR}/7z.txt"

if which clpeak &> /dev/null; then
  clpeak --xml-file "${DIR}/clpeak.xml"
fi
if which cryptsetup &> /dev/null; then
  cryptsetup benchmark > "${DIR}/cryptsetup.txt"
fi

run_geekbench_gpu "5"
run_geekbench_gpu "4"

# TODO: Passmark

./pts/run-tests.sh
