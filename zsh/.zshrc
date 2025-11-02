# -----
# Initial zsh setup
# -----

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc,
# especially before sourcing zgen.zsh, which is slow.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -f "${HOME}/.zgen/init.zsh" && -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
    . "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
    P10K_DELAYED_SETUP=false
else
    P10K_DELAYED_SETUP=true
fi

# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
# This is configured by zgen.
# export ZSH="${HOME}/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
# This is configured by zgen.
# ZSH_THEME="robbyrussell"
# ZSH_THEME="powerlevel10k/powerlevel10k"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to automatically update without prompting.
# DISABLE_UPDATE_PROMPT="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM="${HOME}/.oh-my-zsh/custom2"
ZSH_CUSTOM="${ZDOTDIR}/custom"
# You can also do this with a symbolic link.

# Custom plugin configuration
ZSH_AUTOSUGGEST_USE_ASYNC="true"

if [ ! -d "${HOME}/.zgen" ]; then
    git clone https://github.com/tarjoilija/zgen.git "${HOME}/.zgen"
fi
# This has to be after ZSH_CUSTOM, but before using the zgen command
. "${HOME}/.zgen/zgen.zsh"

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
# plugins=(
#     # Oh my Zsh plugins
#     adb celery cp docker git npm nvm pip pylint rsync ubuntu ufw virtualenv
#     # These have been removed
#     # - django: deprecated
#     # - sudo: was annoying when combined with the autocomplete plugins
#     # Custom plugins
#     zsh-autocomplete
#     zsh-autosuggestions
#     zsh-syntax-highlighting
# )

# If the zgen init script doesn't exist, then configure and generate it.
if ! zgen saved; then
    # Plugins
    zgen oh-my-zsh
    zgen oh-my-zsh plugins/colored-man-pages
    zgen oh-my-zsh plugins/cp
    zgen oh-my-zsh plugins/git  # Git is already required for downloading oh-my-zsh.
    zgen load marlonrichert/zsh-autocomplete
    zgen load zsh-users/zsh-autosuggestions
    zgen load zsh-users/zsh-syntax-highlighting

    # Optional features in alphabetical order
    if command -v adb &> /dev/null; then
        zgen oh-my-zsh plugins/adb
    fi
    if command -v asdf &> /dev/null; then
        zgen oh-my-zsh plugins/asdf
    fi
    if command -v autojump &> /dev/null; then
        zgen oh-my-zsh plugins/autojump
    fi
    if command -v docker &> /dev/null; then
        zgen oh-my-zsh plugins/docker
    fi
    if command -v npm &> /dev/null; then
        zgen oh-my-zsh plugins/npm
    fi
    if command -v nvm &> /dev/null; then
        zgen oh-my-zsh plugins/nvm
    fi
    if command -v python3 &> /dev/null; then
        zgen oh-my-zsh plugins/celery
        zgen oh-my-zsh plugins/pip
        zgen oh-my-zsh plugins/pylint
        zgen oh-my-zsh plugins/virtualenv
    fi
    if command -v rsync &> /dev/null; then
        zgen oh-my-zsh plugins/rsync
    fi
    if command -v screen &> /dev/null; then
        zgen oh-my-zsh plugins/screen
    fi
    if lsb_release -a | grep -q "Ubuntu"; then
        zgen oh-my-zsh plugins/ubuntu
    fi
    if command -v ufw &> /dev/null; then
        zgen oh-my-zsh plugins/ufw
    fi
    if command -v code &> /dev/null; then
        zgen oh-my-zsh plugins/vscode
    fi
    if [ -f "${HOME}/.wakatime.cfg" ]; then
        zgen load sobolevn/wakatime-zsh-plugin
    fi
    if command -v firefox &> /dev/null; then
        zgen oh-my-zsh plugins/web-search
    fi

    # Theme
    zgen load romkatv/powerlevel10k powerlevel10k

    # Generate the init script from plugins above
    zgen save

    # Also configure tmux
    if command -v tmux &> /dev/null && [ ! -f "${HOME}/.config/tmux/tmux.conf" ]; then
        echo "Tmux was found, but it seems not to be configured. Configuring using Oh my tmux!"
        curl -fsSL "https://github.com/gpakosz/.tmux/raw/refs/heads/master/install.sh#$(date +%s)" | bash
    fi
fi

# Delayed Powerlevel10k setup to avoid the warning about console output.
# This has to be after "zgen save"
if [[ "${P10K_DELAYED_SETUP}" = true && -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
    . "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# -----
# Completion
# -----

# From: https://gitlab.com/drjaska-projects/configs/zsh/-/blob/master/.zshrc
# Additional completions from man pages with
# https://github.com/umlx5h/zsh-manpage-completion-generator
# Seems better than above, less faulty files
[[ "${fpath[*]}" == *"$HOME/.local/share/zsh/generated_man_completions"* ]] || \
	[ -d "$HOME/.local/share/zsh/generated_man_completions" ] && \
		fpath+=("$HOME/.local/share/zsh/generated_man_completions")

# Use modern completion system
# At the moment this is too slow, and is therefore currently disabled.
# autoload -U +X compinit && compinit

zstyle ':completion:*' use-compctl false

# show hidden folders/files in completion list
zstyle ':completion:*' hidden false

# _expand completer adds a / after valid directory or space after valid filename, command etc.
zstyle ':completion:*' add-space true

# define message formats for messages from completion
zstyle ':completion:*:warnings' format 'No completion matches with given input'
zstyle ':completion:*:corrections' format '%B%d (errors: %e)%b'
zstyle ':completion:*' format 'Completing %d'
zstyle ':completion:*' auto-description 'specify: %d'

# show more descriptions
zstyle ':completion:*' verbose true

# group completion list by entry types
zstyle ':completion:*:*:-command-:*:commands' \
	group-name commands
zstyle ':completion:*:*:-command-:*:functions' \
	group-name functions
# ^ but don't group
#zstyle ':completion:*' group-name ''

# pasting with tabs doesn't perform completion
zstyle ':completion:*' insert-tab pending

# with commands like `rm' it's annoying if one gets offered the same filename
# again even if it is already on the command line. To avoid that:
zstyle ':completion:*:rm:*' ignore-line yes

# which completers should be called
zstyle ':completion:*' completer _complete _expand _ignored _match _correct _approximate _prefix

# completers will try to match: exact matches, then case sensitive matches,
# then case insensitive matches, then correction, then partial word completions
zstyle ':completion:*' matcher-list '' 'm:{a-z}={A-Z}' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=* l:|=*'

# I don't fully know what these do or if they're optimal :)

# enable arrow key movement and list index visualizer
# for cycling through completion options
# idk what else this does or what other options it has
zstyle ':completion:*' menu select=2


# -----
# Other configs
# -----

# Handled by zgen
# . "${ZSH}/oh-my-zsh.sh"

# User configuration

# Add user scripts to PATH
export PATH="${HOME}/.local/bin:${PATH}"

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi
export EDITOR="nano"

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# Use VSCodium as the default VS Code for the vscode plugin
VSCODE=codium

# Enable the use of "!" without escaping it as "\!"
# For e.g. DuckDuckGo bangs
setopt nobanghist


# -----
# Key bindings
# -----

# select emacs keymap and bind it to main
# zsh now uses emacs keybindings even if our EDITOR is set to vim
# this gives some bash-like keybinds like
# Ctrl+A to beginning of line
# Ctrl+E to end of line
# Ctrl+K kill line from cursor to end
bindkey -e

# bind Ctrl-U to kill line before cursor
bindkey \^U backward-kill-line

# Now the key bindings are
# Ctrl+D exit the terminal
# Ctrl+W kill previous word
# Ctrl+Y paste previously killed
# Ctrl+U kill line before the cursor
# Ctrl+K kill line after the cursor

# You can see the existing key bindings with the command "bindkey"

# Expand glob expressions, subcommands and aliases
# This variable serves as a blacklist
GLOBALIAS_FILTER_VALUES=()
# . ${ZSHLIBPATH}ohmyzsh/plugins/globalias/globalias.plugin.zsh
globalias() {
	# Get last word to the left of the cursor:
	# (z) splits into words using shell parsing
	# (A) makes it an array even if there's only one element
	local word=${${(Az)LBUFFER}[-1]}
	if [[ $GLOBALIAS_FILTER_VALUES[(Ie)$word] -eq 0 ]]; then
		zle _expand_alias
		zle expand-word
	fi
	# zle self-insert #don't type ^@ if bound to ctr+space...
}
zle -N globalias

# Ctrl+space configs
# Expand all aliases, including global
bindkey -M emacs "^ " globalias
bindkey -M viins "^ " globalias
# Ctrl+space as a normal space
bindkey -M emacs " " magic-space
bindkey -M viins " " magic-space
# Normal space during searches
bindkey -M isearch " " magic-space


# -----
# External tools
# -----

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

# Print stderr with red. For more see
# https://github.com/sickill/stderred
STDERRED_PATH="${GIT_DIR}/stderred/lib64/libstderred.so"
if [ -f $STDERRED_PATH ]; then
    export LD_PRELOAD="${STDERRED_PATH}${LD_PRELOAD:+:$LD_PRELOAD}"
    red_colored_text=$(tput setaf 9)
    export STDERRED_ESC_CODE=`echo -e "$red_colored_text"`
else
    # echo "stderred was not found. Please install it or remove it from .zshrc."
fi
unset STDERRED_PATH

# Ruby
# https://jekyllrb.com/docs/installation/ubuntu/
# This has to be before colorls loading, as it uses gem, which is configured here.
export GEM_HOME="$HOME/.gems"
export PATH="${HOME}/.gems/bin:${PATH}"

# Colorls configuration
# https://github.com/athityakumar/colorls
if command -v gem &> /dev/null; then
    COLORLS_FILE_PATH="$(gem which colorls)"
    if [ -f "${COLORLS_FILE_PATH}" ]; then
        COLORLS_PATH="$(dirname "${COLORLS_FILE_PATH}")"
        . "${COLORLS_PATH}/tab_complete.sh"
        alias lc='colorls -lA --sd'
    else
        # echo "Colorls was not found. Please install it with \"gem install colorls\" or remove it form .zshrc."
    fi
    unset COLORLS_FILE_PATH
    unset COLORLS_PATH
else
    # echo "Gem was not found. Please install Ruby."
fi

# Powerline
# https://github.com/powerline/powerline
# If using Powerline, the zsh theme should be disabled
# https://wiki.archlinux.org/index.php/Powerline
# POWERLINE_SCRIPT="/usr/share/powerline/bindings/zsh/powerline.zsh"
# if [ -f $POWERLINE_SCRIPT ]; then
#     powerline-daemon -q
#     . "/usr/share/powerline/bindings/zsh/powerline.zsh"
# fi

# PowerShell telemetry has to be disabled with an environment variable before starting it.
# https://github.com/PowerShell/PowerShell#telemetry
export POWERSHELL_TELEMETRY_OPTOUT="1"

# Powerlevel10k configuration
# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || . ~/.p10k.zsh

# Add Snap icons to the launcher
if [ -f "/etc/profile.d/apps-bin-path.sh" ]; then
    emulate sh -c ". /etc/profile.d/apps-bin-path.sh"
fi

# Fix command-line usage of LibreOffice
# https://askubuntu.com/a/977080/
if [ -d "/usr/lib/libreoffice/program" ]; then
    export LD_LIBRARY_PATH="/usr/lib/libreoffice/program:${LD_LIBRARY_PATH}"
fi

# Fix ROCm OpenCL
# By default clinfo and other OpenCL applications might not see the ROCm driver.
if [ -d "/opt/rocm" ]; then
    # Do not change the configuration on clusters, as they have their own driver setup.
    if command -v srun &> /dev/null; then :; else
        export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/rocm/lib:/opt/rocm/opencl/lib"
    fi
fi

# This prevents the "disk quota exceeded" error when building Apptainer containers on CSC servers.
if [ -z "${TMPDIR}" ]; then
    APPTAINER_CACHEDIR=$TMPDIR
fi

# -----
# Additional repositories
# -----

if [ -f "${GIT_DIR}/vxl-scripts/utils.zsh" ]; then
  . "${GIT_DIR}/vxl-scripts/utils.zsh"
fi

if [ -f "${GIT_DIR}/private-scripts/utils.zsh" ]; then
  . "${GIT_DIR}/private-scripts/utils.zsh"
fi
