# Enable this config by running something like this
# ln -s ~/git/linux-scripts/physics/kale/.bashrc .bashrc

# Enable CMSSW
CMSSW_SCRIPT="${HOME}/git/linux-scripts/physics/kale/cmssw.sh"
if [ -f $CMSSW_SCRIPT ]; then
  source $CMSSW_SCRIPT
fi
unset CMSSW_SCRIPT
