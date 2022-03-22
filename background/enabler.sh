#!/bin/bash -e

if [ "${EUID}" -ne 0 ]; then
  echo "This script should be run as root."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_DIR="$( dirname "${SCRIPT_DIR}" )"

echo "Installing cron job scripts"
mkdir -p /usr/bin/local/agx
cp ./fix-boinc.sh /usr/local/bin/agx/
chmod 755 /usr/local/bin/agx/fix-boinc.sh
echo "Installation ready"
echo "Now add the following to the root crontab with \"sudo crontab -e\"":
echo "@hourly /usr/local/bin/agx/fix-boinc.sh"
echo "You can check whether cron is working properly with:"
echo "grep crontab /var/log/syslog | tail"
source "${REPO_DIR}/venv/bin/activate"
# This may fail, so this should be the last line.
chkcrontab /var/spool/cron/crontabs/root
