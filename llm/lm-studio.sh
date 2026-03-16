#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

"${SCRIPT_DIR}"/LM-Studio-*.appimage --disable-setuid-sandbox --no-sandbox
