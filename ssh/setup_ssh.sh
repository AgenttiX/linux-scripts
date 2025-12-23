#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
. "${SCRIPT_DIR}/setup_common.sh"

echo "Configuring SSH."

echo "Testing whether you have sudo access."
if sudo -l &>/dev/null; then
  echo "You seem to have sudo access. Installing optional packages."
  sudo apt update
  sudo apt install autossh curl mosh openssh-client ssh-askpass tar
  # SSH Guardian Agent
  CPU_ARCH=$(uname -m)
  if [ "${CPU_ARCH}" = "x86_64" ]; then
    echo "x86_64 CPU architecture detected. Installing Guardian Agent."
    curl -L https://api.github.com/repos/StanfordSNR/guardian-agent/releases/latest | grep browser_download_url | grep 'linux' | cut -d'"' -f 4 | xargs curl -Ls | tar xzv
    sudo cp "${SCRIPT_DIR}/sga_linux_amd64"/* /usr/local/bin
  else
    echo "Non-x86_64 CPU architecture (${CPU_ARCH}) detected. Skipping Guardian Agent installation."
  fi
else
  echo "You don't seem to have sudo access. Skipping installation of optional packages."
fi

chmod 700 "${CONF_DIR}"
chmod 600 "${CONF_DIR}/authorized_keys"
if [ -f "${CONF_DIR}/config" ]; then
  chmod 600 "${CONF_DIR}/config"
fi

if [ -L "${SSH_DIR}" ]; then
  echo "SSH folder is already a symlink. Skipping symlink creation."
else
  if [ -d "${SSH_DIR}" ]; then
    echo "Backing up old SSH folder."
    mv "${SSH_DIR}" "${SSH_DIR}-old"
  fi
  echo "Creating symlink to the SSH folder."
  ln -s "${CONF_DIR}" "${SSH_DIR}"
fi

SSH_CONFIG_D_DIR="${SSH_DIR}/config.d"
if [ -L "${SSH_CONFIG_D_DIR}" ]; then
  echo "SSH conf.d folder is already a symlink. Skipping symlink creation."
else
  if [ -d "${SSH_CONFIG_D_DIR}" ]; then
    echo "Backing up old SSH conf.d folder."
    mv "${SSH_CONFIG_D_DIR}" "${SSH_CONFIG_D_DIR}-old"
  fi
  echo "Creating symlink to the SSH config.d folder."
  ln -s "${SCRIPT_DIR}/config.d" "${SSH_CONFIG_D_DIR}"
fi

echo "Creating the controlmasters directory."
mkdir -p "${SSH_DIR}/controlmasters"

# echo "Fixing locales for Mosh."
# https://github.com/mobile-shell/mosh/issues/102#issuecomment-5111502
# sudo sed -i "s/^    SendEnv LANG LC_\*/#   SendEnv LANG LC_\*/g" "/etc/ssh/ssh_config"

echo "SSH configured."
