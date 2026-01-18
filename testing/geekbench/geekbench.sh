#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &> /dev/null && pwd )"
DIR="$(dirname "${SCRIPT_DIR}")/report/geekbench"
mkdir -p "${DIR}"

function run-geekbench-ai() {
  GEEKBENCH_SEARCH=( "${SCRIPT_DIR}/GeekbenchAI"*"/banff_avx2")
  GEEKBENCH="${GEEKBENCH_SEARCH[0]}"
  OUTPUT="${DIR}/geekbench-ai.txt"
  $GEEKBENCH --ai-list |& tee "${OUTPUT}"
  $GEEKBENCH --ai |& tee "${OUTPUT}"
}

function run-geekbench() {
  VERSION=$1
  GEEKBENCH_SEARCH=( "${SCRIPT_DIR}/Geekbench-${VERSION}."*"/geekbench_x86_64" )
  GEEKBENCH="${GEEKBENCH_SEARCH[0]}"
  OUTPUT="${DIR}/geekbench-${VERSION}.txt"
  $GEEKBENCH --sysinfo |& tee "${OUTPUT}"
  $GEEKBENCH --compute-list |& tee -a "${OUTPUT}"
  $GEEKBENCH --cpu  |& tee -a "${OUTPUT}"

  # TODO: process --compute-list and run on all GPUs
  $GEEKBENCH --compute CUDA  |& tee -a "${OUTPUT}"
  $GEEKBENCH --compute OpenCL |& tee -a "${OUTPUT}"

  # The --save option is unavailable without a license
  # --save "${DIR}/geekbench${VERSION}_result_cpu.txt"
  # --save "${DIR}/geekbench${VERSION}_result_cuda.txt"
  # --save "${DIR}/geekbench${VERSION}_result_opencl.txt"
}

run-geekbench-ai
run-geekbench "6"
run-geekbench "5"
run-geekbench "4"
run-geekbench "3"
run-geekbench "2"
