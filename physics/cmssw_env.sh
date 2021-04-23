#!/bin/bash -e

CMSSW_VERSION="10_6_23"
CMSSW_NAME="CMSSW_${CMSSW_VERSION}"

if [[ $* == *--create* ]]; then
  scram p CMSSW $CMSSW_NAME
  cd "${CMSSW_NAME}/src"
  cmsenv
fi

# You may have to run one of these commands separately before copying anything to the src directory

git cms-addpkg Configuration/Eras
git cms-addpkg Configuration/EventContent
git cms-addpkg Configuration/Generator
git cms-addpkg Configuration/Geometry
git cms-addpkg Configuration/StandardSequences
git cms-addpkg Configuration/ProcessModifiers
git cms-addpkg Geometry/CommonDetUnit
git cms-addpkg RecoEgamma

# Build the downloaded packages
scram b -j "$(nproc)"
