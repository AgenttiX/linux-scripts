#!/usr/bin/env bash
set -e

# Before running this script
# - Add an entry like "YOUR_LOCAL_IP hostname.fqdn hostname" to /etc/hosts
# https://wiki.samba.org/index.php/Setting_up_Samba_as_a_Domain_Member#Local_Host_Name_Resolution

# Full instructions
# https://wiki.samba.org/index.php/Setting_up_Samba_as_a_Domain_Member

if [ "${EUID}" -ne 0 ]; then
   echo "This script should be run as root."
   exit 1
fi

if [ -z "$1" ]; then
  echo "Please give the name of the repo containing the config files."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONF_DIR="$(dirname "$(dirname "${SCRIPT_DIR}")")/$1/samba"

if [ ! -d "${CONF_DIR}" ]; then
  echo "Config directory was not found: ${CONF_DIR}"
  exit 1
fi

KRB5_CONF="/etc/krb5.conf"
NSSWITCH_CONF="/etc/nsswitch.conf"
SMB_CONF="/etc/samba/smb.conf"

while true; do
    read -p "Are you going to have domain users log in to this machine (y/n)?" yn
    case $yn in
        [Yy]* ) INSTALL_LOGIN=true; break;;
        [Nn]* ) INSTALL_LOGIN=false; break;;
        * ) echo "Please answer yes or no.";;
    esac
done
# https://wiki.samba.org/index.php/Distribution-specific_Package_Installation#Ubuntu
sudo apt-get update
if $INSTALL_LOGIN; then
  echo "Installing Samba with login support."
  sudo apt-get install acl attr samba samba-dsdb-modules samba-vfs-modules winbind libpam-winbind libnss-winbind libpam-krb5 krb5-config krb5-user
else
  echo "Installing Samba without login support."
  # libnss-winbind is necessary for group policy support.
  sudo apt-get install acl attr samba samba-dsdb-modules samba-vfs-modules winbind libnss-winbind krb5-config krb5-user
fi
echo "Samba version: $(samba --version)"

echo "Testing Samba configuration before applying it. You may see a warning about weak crypto."
echo "It is because of GnuTLS default settings and out of the scope of Samba itself. It is being worked on upstream."
# https://bugzilla.samba.org/show_bug.cgi?id=14583
# https://bugzilla.redhat.com/show_bug.cgi?id=1840754
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=975882
testparm "${CONF_DIR}/smb.conf" --suppress-prompt

if [ ! -f "${KRB5_CONF}.bak" ]; then
  echo "Backing up existing ${KRB5_CONF}"
  cp "${KRB5_CONF}" "${KRB5_CONF}.bak"
else
  echo "Backup of ${KRB5_CONF} already exists."
fi
echo "Configuring Kerberos"
cp "${CONF_DIR}/krb5.conf" "${KRB5_CONF}"
chown root:root "${KRB5_CONF}"
chmod 644 "${KRB5_CONF}"

if [ ! -f "${SMB_CONF}.bak" ]; then
  echo "Backing up existing ${SMB_CONF}"
  cp "${SMB_CONF}" "${SMB_CONF}.bak"
else
  echo "Backup of ${SMB_CONF} already exists."
fi
echo "Configuring Samba"
cp "${CONF_DIR}/smb.conf" "${SMB_CONF}"
chown root:root "${SMB_CONF}"
chmod 644 "${SMB_CONF}"

if [ ! -f "${NSSWITCH_CONF}.bak" ]; then
  echo "Backing up existing ${NSSWITCH_CONF}"
  cp "${NSSWITCH_CONF}" "${NSSWITCH_CONF}.bak"
else
  echo "Backup of ${NSSWITCH_CONF} already exists."
fi
echo "Configuring nsswitch"
# The ^ matches the start of the line and $ matches its end.
sed -i 's/^passwd:         files systemd$/passwd:         files systemd winbind/g' "${NSSWITCH_CONF}"
sed -i 's/^group:          files systemd$/group:          files systemd winbind/g' "${NSSWITCH_CONF}"
echo "-----"
cat "${NSSWITCH_CONF}"
echo "-----"

# systemctl status smbd.service
# systemctl status nmbd.service
# systemctl status winbind.service

echo "Samba version: $(samba --version)"
echo "If Samba version < 4.15.0, join the host to the domain with:"
echo "net ads join -U your-admin-username"
echo "If Samba version >= 4.15.0, join the host to the domain with:"
echo "samba-tool domain join your-domain.example.com MEMBER -U your-admin-username"
echo "Then reboot"
