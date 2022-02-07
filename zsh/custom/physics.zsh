# Enable Geant4
GEANT_SCRIPT="/usr/local/bin/geant4.sh"
if [ -f $GEANT_SCRIPT ]; then
    PWD_BEFORE_GEANT4="$(pwd)"
    cd /usr/local/bin
    source $GEANT_SCRIPT
    cd $PWD_BEFORE_GEANT4
    # PYTHON_VERSION_STR=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    # export PYTHONPATH="${PYTHONPATH}:/usr/local/lib/python${PYTHON_VERSION_STR}/site-packages"
    # unset PYTHON_VERSION_STR
fi
unset GEANT_SCRIPT

# Configure NorduGrid ARC
export X509_CERT_DIR="${HOME}/.globus"

# Pythia 8 Python bindigs are configured in python.zsh

# CERN ROOT
# https://root.cern/
ROOT_SCRIPT="${HOME}/Downloads/root/bin/thisroot.sh"
if [ -f $ROOT_SCRIPT ]; then
    source $ROOT_SCRIPT
fi
unset ROOT_SCRIPT
