#!/usr/bin/env zsh

pull-thesis() {
  OLD_PWD="$(pwd)"
  cd "${HOME}/Git/pttools" || return
  git pull
  cd "${HOME}/Git/msc-thesis2" || return
  git pull
  cd "${OLD_PWD}" || return
}

# Enable Geant4
GEANT_SCRIPT="/usr/local/bin/geant4.sh"
if [ -f "${GEANT_SCRIPT}" ]; then
    PWD_BEFORE_GEANT4="$(pwd)"
    cd "/usr/local/bin" || return 1
    # shellcheck disable=SC1090
    source "${GEANT_SCRIPT}"
    cd "${PWD_BEFORE_GEANT4}" || return 1
    # PYTHON_VERSION_STR=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    # export PYTHONPATH="${PYTHONPATH}:/usr/local/lib/python${PYTHON_VERSION_STR}/site-packages"
    # unset PYTHON_VERSION_STR
fi
unset GEANT_SCRIPT

# Configure NorduGrid ARC
export X509_CERT_DIR="${HOME}/.globus"

# Pythia 8 Python bindings are configured in python.zsh

# CERN ROOT
# https://root.cern/
ROOT_SCRIPT="${HOME}/Downloads/root/bin/thisroot.sh"
if [ -f "${ROOT_SCRIPT}" ]; then
    # shellcheck disable=SC1090
    source "${ROOT_SCRIPT}"
fi
unset ROOT_SCRIPT

ZOTERO_SCRIPT="${HOME}/Downloads/Zotero/Zotero_linux-x86_64/zotero"
if [ -f "${ZOTERO_SCRIPT}" ]; then
  # shellcheck disable=SC2139
  alias zotero="${ZOTERO_SCRIPT}"
fi
unset ZOTERO_SCRIPT
