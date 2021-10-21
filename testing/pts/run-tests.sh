#!/bin/bash -e
# TODO: Work in progress

mkdir /results
/phoronix-test-suite/phoronix-test-suite system-info 2>&1 | tee /results/system-info.txt
/phoronix-test-suite/phoronix-test-suite system-sensors 2>&1 | tee /results/system-sensors.txt
/phoronix-test-suite/phoronix-test-suite diagnostics 2>&1 | tee /results/system-sensors.txt
