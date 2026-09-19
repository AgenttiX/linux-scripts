#!/usr/bin/env zsh

kill-user-processes() {
  # Kill the processes of the current user whose full command line matches an extended regex.
  # -----
  # Only the processes of the current user are killed, so that this is safe to use
  # on computers that are shared with other users, and so that a too broad pattern
  # can't take down the processes of the system or of someone else.
  # The processes are first asked to quit with SIGTERM,
  # and only the ones that don't quit within the grace period are killed with SIGKILL.
  # -----
  # Usage: kill-user-processes NAME PATTERN [-n|--dry-run] [-y|--yes]
  local NAME="${1:?Usage: $0 NAME PATTERN [-n|--dry-run] [-y|--yes]}"
  local PATTERN="${2:?Usage: $0 NAME PATTERN [-n|--dry-run] [-y|--yes]}"
  shift 2

  local DRY_RUN=0
  local ASSUME_YES=0
  local ARG
  for ARG in "$@"; do
    case "${ARG}" in
      -n | --dry-run) DRY_RUN=1 ;;
      -y | --yes) ASSUME_YES=1 ;;
      *)
        echo "Unknown option: \"${ARG}\"" >&2
        return 2
        ;;
    esac
  done

  # "pgrep -u" limits the search to the processes of the current user.
  # The PIDs of this shell and of its parent are dropped,
  # so that a pattern that happens to match them can't kill the terminal.
  local -a PIDS
  local PID
  for PID in ${(f)"$(pgrep -u "$(id -u)" -f -- "${PATTERN}")"}; do
    if [[ "${PID}" == <-> ]] && [ "${PID}" != "$$" ] && [ "${PID}" != "${PPID}" ]; then
      PIDS+=("${PID}")
    fi
  done

  if [ "${#PIDS}" -eq 0 ]; then
    echo "No ${NAME} processes of user \"$(id -un)\" are running."
    return 0
  fi

  echo "The following ${NAME} processes of user \"$(id -un)\" were found:"
  ps -o pid,etime,rss,comm -p "${(j:,:)PIDS}"

  if [ "${DRY_RUN}" -ne 0 ]; then
    echo "This is a dry run, so the processes are not killed."
    return 0
  fi

  if [ "${ASSUME_YES}" -eq 0 ]; then
    local ANSWER
    # This fails when there is no terminal to ask from, which aborts the killing.
    read -r "ANSWER?Kill these ${#PIDS} processes? [y/N] "
    case "${ANSWER}" in
      y | Y | yes | YES) ;;
      *)
        echo "Aborted."
        return 1
        ;;
    esac
  fi

  kill -TERM "${PIDS[@]}" 2> /dev/null

  # Give the processes 10 seconds to quit cleanly before they are killed.
  local -a REMAINING
  local ROUND
  for ROUND in {1..20}; do
    REMAINING=()
    for PID in "${PIDS[@]}"; do
      if kill -0 "${PID}" 2> /dev/null; then
        REMAINING+=("${PID}")
      fi
    done
    if [ "${#REMAINING}" -eq 0 ]; then
      break
    fi
    sleep 0.5
  done

  if [ "${#REMAINING}" -ne 0 ]; then
    echo "Killing ${#REMAINING} ${NAME} processes that did not quit."
    kill -KILL "${REMAINING[@]}" 2> /dev/null
  fi
}

kill-pycharm() {
  # Kill the PyCharm processes of the current user.
  # -----
  # The PyCharm windows that are used for SSH remoting to a server
  # sometimes freeze on the client computer and have to be killed.
  # The pattern covers the JetBrains Gateway, the thin client (JetBrainsClient),
  # a locally running PyCharm, and their helper processes
  # such as fsnotifier and the JCEF browser.
  # The JetBrains Toolbox daemon is intentionally not matched,
  # since it is not a part of a PyCharm window.
  # -----
  # Only the processes of the current user are killed,
  # so this does not disturb the other users of the computer,
  # nor the IDE backend that runs on the server.
  # -----
  # Usage: kill-pycharm [-n|--dry-run] [-y|--yes]
  kill-user-processes "PyCharm" \
    'pycharm|PyCharm|jetbrains_client|JetBrainsClient|jetbrains-gateway|JetBrainsGateway' "$@"
}

# function nvidia-smi {
#   # This fix is no longer needed and won't work with the latest Nvidia drivers (570->).
#   # https://forums.developer.nvidia.com/t/nvidia-smi-uses-all-of-ram-and-swap/295639/3
#   valgrind nvidia-smi "$@" 2> /dev/null
# }
