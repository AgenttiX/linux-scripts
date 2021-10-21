#!/bin/bash -e

if [ "${EUID}" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

# This already runs apt-get update
source ./report.sh

if ! which speedtest > /dev/null; then
  curl -s https://install.speedtest.net/app/cli/install.deb.sh | sudo bash
fi
sudo apt-get install sysbench speedtest stress-ng wget

./geekbench/download_geekbench.sh

speedtest |& tee "${DIR}/speedtest.txt"
7z b -mmt1 |& tee "${DIR}/7z_single_thread.txt"
7z b |& tee "${DIR}/7z.txt"

GEEKBENCH_SEARCH=( "${SCRIPT_DIR}/geekbench/Geekbench-5."*"/geekbench_x86_64" )
GEEKBENCH_5="${GEEKBENCH_SEARCH[0]}"
$GEEKBENCH_5 --sysinfo |& tee "${DIR}/geekbench5.txt"
$GEEKBENCH_5 --compute-list |& tee -a "${DIR}/geekbench5.txt"
$GEEKBENCH_5 --cpu --save "${DIR}/geekbench5_result_cpu.txt" |& tee -a "${DIR}/geekbench5.txt"
$GEEKBENCH_5 --compute CUDA --save "${DIR}/geekbench5_result_cuda.txt" |& tee -a "${DIR}/geekbench5.txt"
$GEEKBENCH_5 --compute OpenCL --save "${DIR}/geekbench5_result_opencl.txt"|& tee -a "${DIR}/geekbench5.txt"

GEEKBENCH_SEARCH=( "${SCRIPT_DIR}/geekbench/Geekbench-4."*"/geekbench_x86_64" )
GEEKBENCH_4="${GEEKBENCH_SEARCH[0]}"
$GEEKBENCH_4 --sysinfo |& tee "${DIR}/geekbench4.txt"
$GEEKBENCH_4 --compute-list |& tee -a "${DIR}/geekbench4.txt"
$GEEKBENCH_4 --cpu --save "${DIR}/geekbench4_result_cpu.txt" |& tee -a "${DIR}/geekbench4.txt"
$GEEKBENCH_4 --compute CUDA --save "${DIR}/geekbench4_result_cuda.txt" |& tee -a "${DIR}/geekbench4.txt"
$GEEKBENCH_4 --compute OpenCL --save "${DIR}/geekbench4_result_opencl.txt"|& tee -a "${DIR}/geekbench4.txt"
