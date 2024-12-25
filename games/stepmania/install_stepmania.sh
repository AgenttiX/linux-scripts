#!/usr/bin/env sh
set -eu

# This script configures StepMania dependencies for Ubuntu.

# Download StepMania here:
# https://www.stepmania.com/download/

# Songs
# https://search.stepmaniaonline.net/

# This PPA does not work on Ubuntu 24.10,
# as it contains dependencies to old packages.
# https://launchpad.net/~ubuntuhandbook1/+archive/ubuntu/stepmania

# https://www.reddit.com/r/Stepmania/comments/bkmy8q/stepmania_isnt_opening_on_linux/
# https://www.codeweavers.com/support/forums/general/?t=26;mhl=149152;msg=149152
sudo apt-get install libjpeg62 libpcre3

# https://github.com/stepmania/stepmania/issues/2186#issuecomment-1079837345
sudo ln -s "/lib/x86_64-linux-gnu/libva.so.2" "/lib/x86_64-linux-gnu/libva.so.1"
