#!/bin/sh -e

# Based on the instructions at
# https://www.mv.helsinki.fi/home/slehti/ComputingMethodsInHEP/ComputingMethodsInHEP.html
# https://www.mv.helsinki.fi/home/slehti/ComputingMethodsInHEP/CompInHEP_lect11.pdf

# This script must be sourced for the configuration to activate to the current shell
# "source ./cmssw.sh"

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source ${VO_CMS_SW_DIR}/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc830
