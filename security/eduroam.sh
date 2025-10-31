#!/usr/bin/env sh
set -eu

openssl x509 -noout -text -in "${HOME}/.local/share/geteduroam/ca-cert.pem"
