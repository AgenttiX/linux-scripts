#!/usr/bin/sh -e

# Disable log spam
# https://unix.stackexchange.com/a/230442
export NO_AT_BRIDGE=1

# Sound does not yet work in the Snap package.
# https://github.com/ahimta/epsxe-tools#known-issues
epsxe -nosound
