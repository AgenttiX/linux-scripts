#!/usr/bin/env zsh

update() {
  if (command -v apt &> /dev/null); then
    echo "Updating apt packages"
    sudo apt update
    # Remove unused packages before upgrading to prevent unnecessary upgrades
    sudo apt autoremove
    sudo apt dist-upgrade
    sudo apt autoremove
  fi
  if (command -v snap &> /dev/null); then
    echo "Updating Snap packages"
    sudo snap refresh
  fi
  if (command -v flatpak &> /dev/null); then
    echo "Updating Flatpak packages"
    # Remove unused packages before updating to prevent unnecessary updates
    flatpak uninstall --unused
    flatpak update
    flatpak uninstall --unused
  fi

  # Git repositories
  local PWD_BEFORE_UPDATE="${PWD}"
  if [ -d "${HOME}/Git/agx-ai" ]; then
    echo "Updating agx-ai"
    cd "${HOME}/Git/agx-ai"
    git pull
  fi
  if [ -d "${HOME}/Git/linux-scripts" ]; then
    echo "Updating linux-scripts"
    cd "${HOME}/Git/linux-scripts"
    git pull
  fi
  if [ -d "${HOME}/Git/private-scripts" ]; then
    echo "Updating private-scripts"
    cd "${HOME}/Git/private-scripts"
    git pull
  fi
  if [ -d "${HOME}/Git/vxl-scripts" ]; then
    echo "Updating vxl-scripts"
    cd "${HOME}/Git/vxl-scripts"
    git pull
  fi
  if [ -d "${HOME}/Git/windows-scripts" ]; then
    echo "Updating windows-scripts"
    cd "${HOME}/Git/windows-scripts"
    git pull
  fi
  cd "${PWD_BEFORE_UPDATE}"

  # This should be after the Git repo pulling,
  # since the repos can have an updated zsh config.
  if (command -v zgen &> /dev/null); then
    echo "Updating zgen"
    zgen update
  fi

  if command -v claude; then
    echo "Updating Claude"
    claude update
  fi
  if command -v kilo; then
    echo "Upgrading Kilo Code"
    kilo upgrade
  fi
  if command -v lms; then
    echo "Updating LM Studio runtimes"
    lms runtime update --all
  fi
  if command -v rustup; then
    echo "Updating Rust"
    rustup update
  fi

  # zsh completions using zsh-manpage-completion-generator
  # Based on:
  # https://gitlab.com/drjaska-projects/configs/zsh/-/blob/master/.zshrc
  if command -v fish &> /dev/null; then
    local FISH_COMPLETION_DIR="${XDG_DATA_HOME-$HOME}/.local/share/fish/generated_completions"

    echo "Downloading zsh-manpage-completion-generator."
    cd "${ZSH_CUSTOM}"
    curl -sSL "https://github.com/umlx5h/zsh-manpage-completion-generator/releases/latest/download/zsh-manpage-completion-generator_$(uname -s)_$(uname -m).tar.gz" \
      | tar xz "zsh-manpage-completion-generator"
    chmod a+x "${ZSH_CUSTOM}/zsh-manpage-completion-generator"

    echo "Creating fish completions."
    fish -c "fish_update_completions"

    echo "Converting fish completions to zsh completions."
    ./zsh-manpage-completion-generator
    cd "${PWD_BEFORE_UPDATE}"

    # You can disable the completions for specific commands by deleting the files here.
    # rm "${FISH_COMPLETION_DIR}/_git*"
  else
      # echo "Please install fish for zsh-manpage-completion-generator" > /dev/stderr
  fi
}
