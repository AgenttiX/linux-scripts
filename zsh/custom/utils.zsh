#!/usr/bin/env zsh

# TODO: Think whether to use hyphens or underscores in the names.
# Hyphens are probably better, since they're easire to write.
# https://unix.stackexchange.com/a/168222/

apt-rdepends-installed() {
  # Find installed apt packages which depend on argument(s)
  # From:
  # https://gitlab.com/drjaska-projects/configs/zsh/-/blob/master/.zshrc
	apt-cache rdepends "$@" | grep "  " | xargs apt list --installed
}

per-user-usage() {
  # Print the total CPU and RAM usage of the processes of each user.
  # Useful on shared servers with multiple users running processes over SSH.
  {
    printf "%-20s %8s %8s\n" "USER" "%CPU" "%MEM"
    ps -eo user:20,%cpu,%mem --no-headers \
      | awk '{ cpu[$1] += $2; mem[$1] += $3 } END { for (user in cpu) printf "%-20s %8.1f %8.1f\n", user, cpu[user], mem[user] }' \
      | sort -k2 -rn
  }
}

cld() {
  # Claude remote control with automatic virtualenv activation
  if [ -f "./venv/bin/activate" ]; then
    . ./venv/bin/activate
  fi
  claude rc
}

clear-history() {
  "${HOME}/Git/linux-scripts/security/clear_history.sh"
}

fix-kde() {
  killall plasmashell -9
  sleep 1
  kstart plasmashell
}

fix-kde-hard() {
  rm -rf "${HOME}/.cache/"*plasma*
  kwin_wayland --replace &
}

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

# Chats
start-chats() {
  # Start chat clients
  # The "&!" is zsh-specific
  # https://askubuntu.com/a/10557/
  if (command -v discord &> /dev/null); then
    if pgrep -x "Discord" > /dev/null; then :; else
      echo "Starting Discord"
      discord &> /dev/null &!
    fi
  fi
  if command -v flatpak &> /dev/null; then
    if pgrep -x "ferdium" > /dev/null; then :; else
      echo "Starting Ferdium"
      flatpak run org.ferdium.Ferdium &!
    fi
    if pgrep -f "mattermost-desktop" > /dev/null; then :; else
      echo "Starting Mattermost"
      flatpak run org.mattermost.Desktop &!
    fi
    if pgrep -f "telegram-desktop" > /dev/null; then :; else
      echo "Starting Telegram"
      flatpak run org.telegram.desktop &!
    fi
  fi
  if command -v signal-desktop &> /dev/null; then
    if pgrep -f "signal-desktop" > /dev/null; then :; else
      echo "Starting Signal"
      signal-desktop --start-in-tray &> /dev/null &!
    fi
  fi
}

close-chats() {
  # Close chat clients
  # Ferdium may require two signals to fully close.
  # Therefore it's the first to give it as much time as possible to close cleanly.
  killall --signal TERM ferdium 2> /dev/null
  killall --signal TERM Discord 2> /dev/null
  # The "telegram-deskto" is not a typo.
  killall --signal TERM telegram-deskto 2> /dev/null
  killall --signal TERM signal-desktop 2> /dev/null
  killall --signal TERM walc 2> /dev/null
  # Second attempt to close Ferdium
  killall --signal TERM ferdium 2> /dev/null
}

retry_until() {
  # From:
  # https://gitlab.com/drjaska-projects/configs/zsh/-/blob/master/.zshrc
	if [ "$2" = "" ]; then
		echo "Usage: $0 sleeptime command"
	fi

	local sleeptime="$1"
	shift

	until $@
	do
		sleep "$sleeptime"
	done
}

# For those familiar with Vim
alias :q="exit"

# Analyze the contents of a Docker image
# https://github.com/wagoodman/dive
alias dive="docker run -ti --rm  -v /var/run/docker.sock:/var/run/docker.sock docker.io/wagoodman/dive"

# Calculate checksum for current directory INCLUDING filenames and permissions. It takes no arguments
alias dirsum1="tar c . | md5sum"

# Calculate checksum for current directory NOT INCLUDING filenames and permissions. It takes no arguments
alias dirsum2="find . -type f -name '*' -exec md5sum {} + | awk '{print $1}' | sort | md5sum"

# Scan wifi networks. This also refreshes the wifi-list, so if device was not connected,
# it makes auto-connection quicker
alias fix-wifi="sudo iwlist scan | grep 'Cell\|ESSID:\|Quality='"

# shellcheck disable=SC2139
alias modem="sudo ${HOME}/Git/linux-scripts/modem.py"

# if ! command -v nvim &> /dev/null && command -v flatpak; then
#   alias nvim="flatpak run io.neovim.nvim"
# fi

# A joke for typoing the command "apt".
# The "; :" discards any additional arguments.
alias pat="image headpat; :"

# Easy pinging
alias pingu="ping -c 4 google.com"
alias pingu6="ping6 -c 4 google.com"

# Protontricks
# https://github.com/Matoking/protontricks
alias protontricks="flatpak run com.github.Matoking.protontricks"

if ! command -v rocm-smi &> /dev/null && [ -f "/opt/rocm/bin/rocm-smi" ]; then
  alias rocm-smi="/opt/rocm/bin/rocm-smi"
fi

# RTFM = Read The Fucking Manual :D
alias rtfm="man"

alias screeni="screen -rD || screen"

# Fun sudo aliases
alias fuck="sudo"
alias fucking="sudo"
alias please="sudo"

# Google Translate
alias translate="ddg \!translate ${@}"

alias yoink="git pull"
alias yeet="git push"
