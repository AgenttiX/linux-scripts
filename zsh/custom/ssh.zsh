#!/usr/bin/env zsh

mosh() {
  local HOST="${1:?Usage: $0 HOST [mosh args...]}"
  shift || true

  local MOSH_PATH="$(whence -p mosh)"
  # These may also be necessary:
  # -T -o ClearAllForwardings=yes
  local MOSH_SSH_OPTIONS="-o ExitOnForwardFailure=no -o ForwardAgent=no"
  # If RemoteCommand is non-empty, override it for the SSH that mosh uses.
  if [[ -n "$(ssh-remote-command $HOST)" ]]; then
    "${MOSH_PATH}" --ssh="ssh ${MOSH_OPTIONS} -o RemoteCommand=none -o RequestTTY=no" -- "${HOST}" "$@"
  else
    "${MOSH_PATH}" --ssh="ssh ${MOSH_OPTIONS}" -- "${HOST}" "$@"
  fi
}

ssh-remote-command() {
  local HOST="${1:?Usage: $0 HOST}"
  shift || true
  # Ask ssh what it would do after config expansion.
  # ssh -G prints: "remotecommand <value>" (empty if none; may also be absent on some versions)
  return "$(ssh -G -- "$HOST" 2>/dev/null | awk 'tolower($1)=="remotecommand" { $1=""; sub(/^ /,""); print; exit }')"
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
