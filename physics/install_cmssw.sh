#!/usr/bin/bash -e
# Installation script for the CMS software
# https://cms-sw.github.io/
# Based on
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SDTCMSSW_aptinstaller

# Does not work yet on Ubuntu!
# "Error while seeding rpm database with system packages."
# Proper Ubuntu installation instructions are behind a CERN login
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SDTCMSSW_aptinstaller#Ubuntu

# Attempting to install CMSSW as root will result in
# "*** CMS SOFTWARE INSTALLATION ABORTED ***"
# "CMS software cannot be installed as the super-user."
if [ "$EUID" -eq 0 ]; then
  echo "This script should not be run as root."
  exit
fi

export VO_CMS_SW_DIR="/usr/local/cmssw"
sudo mkdir -p $VO_CMS_SW_DIR
sudo chown -R $USER:$USER $VO_CMS_SW_DIR
wget -O "${VO_CMS_SW_DIR}/bootstrap.sh" "http://cmsrep.cern.ch/cmssw/repos/bootstrap.sh"
export SCRAM_ARCH=slc7_amd64_gcc820

# This is "sh" in the documentation, but that would result in the necessary command "source" being undefined
# https://askubuntu.com/questions/504546/error-message-source-not-found-when-running-a-script
bash -x "${VO_CMS_SW_DIR}/bootstrap.sh" setup -path "${VO_CMS_SW_DIR}" -arch "${SCRAM_ARCH}" >& "${VO_CMS_SW_DIR}/bootstrap_${SCRAM_ARCH}.log"
