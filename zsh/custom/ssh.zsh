#!/usr/bin/env zsh

ssh-refresh-master() {
  # Close the SSH ControlMaster connection to a host if it has gone stale.
  # -----
  # A master connection survives suspending the client computer, but its TCP connection does not.
  # Such a master still answers "ssh -O check", and every new session that is multiplexed over it
  # inherits its dead agent forwarding and X11 forwarding.
  # This is why $SSH_AUTH_SOCK stops working in tmux and why GUI programs can't be opened,
  # until the master connection is closed with "ssh -O stop HOST" by hand.
  # "-O stop" is used instead of "-O exit", so that a false positive can't kill the sessions
  # that are still running over the master connection in other terminals.
  # It makes the master stop accepting new sessions and remove its socket,
  # after which the next connection creates a new master.
  # Closing it here removes the need to do that manually,
  # while still keeping the speed-up that ControlMaster provides for healthy connections.
  local HOST="${1:?Usage: $0 HOST}"
  local SSH_PATH="$(whence -p ssh)"

  # There is nothing to refresh if the host has no master connection,
  # or if ControlMaster is not in use at all, as is the case on Windows.
  "${SSH_PATH}" -O check -- "${HOST}" &> /dev/null || return 0

  # Probe the master connection with a short-lived session that checks the forwarded agent.
  # X11 forwarding is disabled for the probe,
  # so that it does not reserve the display number that the actual session should get.
  # The result is read from the exit status instead of the output, because the master connection
  # keeps a copy of the file descriptors of every session that it starts,
  # and would therefore hold a pipe open even after "timeout" has killed the probe.
  timeout 10 "${SSH_PATH}" \
    -T \
    -o BatchMode=yes \
    -o ForwardX11=no \
    -o RemoteCommand=none \
    -o RequestTTY=no \
    -- "${HOST}" 'ssh-add -l > /dev/null 2>&1' < /dev/null &> /dev/null
  local PROBE_STATUS=$?

  local FORWARD_AGENT="$("${SSH_PATH}" -G -- "${HOST}" 2> /dev/null | awk '$1 == "forwardagent" { print $2 }')"

  # ssh passes the exit status of the remote command through,
  # and uses 255 for its own errors. "timeout" uses 124 when it has to kill the probe.
  local REASON=""
  case "${PROBE_STATUS}" in
    # 0: the forwarded agent has keys loaded.
    # 1: the forwarded agent is reachable, but has no keys loaded.
    # 127: the server does not have "ssh-add" installed.
    0 | 1 | 127) ;;
    # 2: "ssh-add" could not reach the forwarded agent.
    2)
      if [ "${FORWARD_AGENT}" = "yes" ]; then
        REASON="its agent forwarding is broken"
      fi
      ;;
    *) REASON="it no longer responds" ;;
  esac

  if [ -n "${REASON}" ]; then
    echo "Closing the stale SSH master connection to \"${HOST}\", because ${REASON}."
    if ! timeout 10 "${SSH_PATH}" -O stop -- "${HOST}" &> /dev/null; then
      echo "Warning: Failed to close the SSH master connection to \"${HOST}\"."
    fi
  fi
}

assh() {
  # AutoSSH wrapper that also refreshes the CSC SSH certificate
  # -----
  # Depending on the type of your SSH key,
  # either the CSC certificate helper tool will activate the certificate automatically,
  # or you may have to configure the "CertificateFile" option in your SSH config.
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
  # Drop the master connection first if it has gone stale,
  # so that agent forwarding and X11 forwarding keep working after the client computer has slept.
  ssh-refresh-master "$1"

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

  # The default `-o idmap=none` may result in the git warning `fatal: detected dubious ownership`.
  # This can be fixed with `-o idmap=user`.
  # However, it's probably better in the long term to use
  # `git config --global --add safe.directory PATH_TO_REPOSITORY` instead to fix this.

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
  ssh -G -- "$HOST" 2>/dev/null | awk 'tolower($1)=="remotecommand" { $1=""; sub(/^ /,""); print; exit }'
}

alias asshfs="autosshfs"
