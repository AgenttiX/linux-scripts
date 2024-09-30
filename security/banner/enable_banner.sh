#!/usr/bin/env bash
set -e

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

# From:
# https://help.ubuntu.com/community/StricterDefaults#SSH_Welcome_Banner
# https://www.cryptsus.com/blog/how-to-secure-your-ssh-server-with-public-key-elliptic-curve-ed25519-crypto.html
cp ./issue.net /etc/issue.net
chmod 744 /etc/issue.net
sed -i '/^#Banner .*/a Banner \/etc\/issue.net' /etc/ssh/sshd_config
systemctl restart ssh.service
systemctl status ssh.service
