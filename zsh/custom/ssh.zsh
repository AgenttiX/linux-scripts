#!/usr/bin/env zsh

assh() {
  # AutoSSH wrapper that also refreshes the CSC SSH certificate
  # -----
  # If you get mysterious errors when using the CSC certificate helper tool,
  # please try downloading the key once manually from MyCSC first.
  local SSH_SETTINGS="$(ssh -G $1)"
  local SSH_HOSTNAME="$(awk '$1 == "hostname" { print $2 }' <<< "$SSH_SETTINGS")"
  if [[ $SSH_HOSTNAME == "roihu"*"csc.fi" ]]; then
    # Edit these according to the location of the CSC certificate helper tool.
    local GIT_DIR="$(dirname "$(dirname "${ZDOTDIR}")")"
    local CSC_CERT_TOOL="${GIT_DIR}/certificate-helper-tool/csc_cert.py"

    if [ -f "${CSC_CERT_TOOL}" ]; then
      local SSH_USER="$(awk '$1 == "user" { print $2 }' <<< "$SSH_SETTINGS")"

      # Edit these according to the naming convention of your SSH keys.
      local STRIPPED_HOSTNAME="${HOST%"-kubuntu"}"
      local SSH_KEY_NAME="id_rsa_tpm_${STRIPPED_HOSTNAME}"

      local SSH_KEY_PATH="${HOME}/.ssh/${SSH_KEY_NAME}.pub"
      if [ -f "${SSH_KEY_PATH}" ]; then
        "${CSC_CERT_TOOL}" -u "${SSH_USER}" "${SSH_KEY_PATH}"
      fi
    else
      echo "CSC certificate helper tool was not found at \"${CSC_CERT_TOOL}\". Please ensure it's installed. You can download it here:"
      echo "https://github.com/CSCfi/certificate-helper-tool"
    fi
  fi
  # If you don't have autossh installed, please install it with e.g. "apt install autossh",
  # or replace "autossh" on the line below with "ssh".
  autossh "$@"
}

autosshfs() {
  # local REMOTE="${1:?Usage: $0 HOST [sshfs args...]}"
  # shift || true
  # local HOST="${REMOTE%%:*}"

  local SSHFS_PATH="$(whence -p sshfs)"
  # If RemoteCommand is non-empty, override it for the SSH that sshfs uses.
  # if [[ -n "$(ssh-remote-command $HOST)" ]]; then
  # "${SSHFS_PATH}" -o ssh_command="ssh -o RemoteCommand=none" "${REMOTE}" "$@"
  # else
  #   "${SSHFS_PATH}" "${REMOTE}" "$@"
  # fi

  # -o compression=no \
  "${SSHFS_PATH}" \
    -o dir_cache=yes \
    -o follow_symlinks \
    -o max_conns=4 \
    -o reconnect \
    -o ssh_command="ssh -o RemoteCommand=none" \
    "$@"
}

mosh() {
  local HOST="${1:?Usage: $0 HOST [mosh args...]}"
  shift || true

  local MOSH_PATH="$(whence -p mosh)"
  # These may also be necessary:
  # -T -o ClearAllForwardings=yes
  local MOSH_SSH_OPTIONS="-o ExitOnForwardFailure=no -o ForwardAgent=no"
  # If RemoteCommand is non-empty, override it for the SSH that mosh uses.
  if [[ -n "$(ssh-remote-command $HOST)" ]]; then
    "${MOSH_PATH}" --ssh="ssh ${MOSH_SSH_OPTIONS} -o RemoteCommand=none -o RequestTTY=no" -- "${HOST}" "$@"
  else
    "${MOSH_PATH}" --ssh="ssh ${MOSH_SSH_OPTIONS}" -- "${HOST}" "$@"
  fi
}

ssh-remote-command() {
  local HOST="${1:?Usage: $0 HOST}"
  shift || true
  # Ask ssh what it would do after config expansion.
  # ssh -G prints: "remotecommand <value>" (empty if none; may also be absent on some versions)
  return "$(ssh -G -- "$HOST" 2>/dev/null | awk 'tolower($1)=="remotecommand" { $1=""; sub(/^ /,""); print; exit }')"
}

alias asshfs="autosshfs"
