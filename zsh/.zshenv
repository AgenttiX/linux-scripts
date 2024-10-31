ZDOTDIR="${HOME}/Git/linux-scripts/zsh"

if [ -f "${HOME}/.cargo/env" ]; then
  . "${HOME}/.cargo/env"
fi

# Pre-startup scripts don't seem to work on Plasma Wayland,
# and therefore the pre-startup script has to be loaded here.
# . "${HOME}/Git/linux-scripts/startup/agx-user-pre-startup.sh"
if [ -f "${HOME}/.ssh-agent-info" ]; then
  eval "$(<"${HOME}/.ssh-agent-info")" > /dev/null
fi
