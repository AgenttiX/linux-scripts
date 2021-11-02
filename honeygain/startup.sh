#!/bin/sh -e
echo "Starting Honeygain with email \"${EMAIL}\" on device \"${DEVICE}\""
./honeygain -tou-accept -email "${EMAIL}" -pass "${PASS}" -device "${DEVICE}"
