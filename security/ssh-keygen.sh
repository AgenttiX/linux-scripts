#!/usr/bin/sh -e

# This script is trivial and mostly a note for myself.
# As of 2021, the default key length of ssh-keygen is 3072 bits, but
# previously it used to be 2048 bits.
# For additional security such as quantum resistance, one should
# use longer keys than the default.
# https://wiki.archlinux.org/index.php/SSH_keys
# https://security.stackexchange.com/questions/143442/what-are-ssh-keygen-best-practices
# https://stribika.github.io/2015/01/04/secure-secure-shell.html
# https://en.wikipedia.org/wiki/Key_size

# When running, don't accidentally overwrite your existing keys!
ssh-keygen -t rsa -b 4096
