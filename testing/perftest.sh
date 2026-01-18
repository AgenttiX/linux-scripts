#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &> /dev/null && pwd )"
DIR="${SCRIPT_DIR}/report"

# This already runs apt update
source ./report.sh --no-report --no-security

# Installers

# The speedtest repo is not kept up to date with the latest Ubuntu versions.
# if ! command -v speedtest > /dev/null; then
#   curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
# fi
# sudo apt update
sudo apt install sysbench stress-ng wget

./geekbench/download_geekbench.sh

if ! command -v phoronix-test-suite &> /dev/null; then
  FILENAME="phoronix-test-suite_10.8.4_all.deb"
  FILE_PATH="${SCRIPT_DIR}/${FILENAME}"
  wget "https://phoronix-test-suite.com/releases/repo/pts.debian/files/${FILENAME}" -O "${FILE_PATH}"
  sudo apt install "${FILE_PATH}"
  # rm "${FILE_PATH}"
  phoronix-test-suite openbenchmarking-login
  phoronix-test-suite batch-setup
fi
phoronix-test-suite openbenchmarking-refresh

# Tests

if command -v speedtest &> /dev/null; then
  speedtest |& tee "${DIR}/speedtest.txt"
else
  echo "Speedtest was not found."
fi

# These are managed by PTS
# 7z b -mmt1 |& tee "${DIR}/7z_single_thread.txt"
# 7z b |& tee "${DIR}/7z.txt"

if command -v clpeak &> /dev/null; then
  echo "Running clpeak OpenCL benchmark."
  clpeak --xml-file "${DIR}/clpeak.xml" |& tee "${DIR}/clpeak.txt"
fi
if command -v cryptsetup &> /dev/null; then
  echo "Running cryptsetup benchmark."
  cryptsetup benchmark |& tee "${DIR}/cryptsetup.txt"
fi

# TODO: Passmark

"${SCRIPT_DIR}/geekbench/geekbench.sh"

./pts/run-tests.sh
