#!/usr/bin/env sh
set -eu

# TODO: Work in progress

. ./ethminer_config.sh

MINER="./teamredminer/teamredminer"
$MINER --list_devices

$MINER \
  --algo=ethash \
  --log_file=autotune_full_log.txt \
  --url="stratum+ssl://${SERVER}:${PORT}" \
  --user="${ADDRESS}" \
  --eth_stratum_mode="ethproxy"
  # --auto_tune=SCAN \
  # --auto_tune_runs=6 \
