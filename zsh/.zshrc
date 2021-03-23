# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
# ZSH_THEME="robbyrussell"
ZSH_THEME="powerlevel10k/powerlevel10k"

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
ZSH_CUSTOM="$HOME/.oh-my-zsh/custom2"
# You can also do this with a symbolic link

# Custom plugin configuration
ZSH_AUTOSUGGEST_USE_ASYNC="true"

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
    # Oh my Zsh plugins
    adb celery cp django docker git npm nvm pip pylint rsync sudo ubuntu ufw virtualenv
    # Custom plugins
    zsh-autocomplete
    zsh-autosuggestions
    zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh

# User configuration

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

# Print stderr with red. For more see
# https://github.com/sickill/stderred
STDERRED_PATH="$HOME/Git/stderred/lib64/libstderred.so"
if [ -f $STDERRED_PATH ]; then
    export LD_PRELOAD="${STDERRED_PATH}${LD_PRELOAD:+:$LD_PRELOAD}"
    red_colored_text=$(tput setaf 9)
    export STDERRED_ESC_CODE=`echo -e "$red_colored_text"`
else
    echo "stderred was not found. Please install it or remove it from .zshrc."
fi

# Colorls configuration
# https://github.com/athityakumar/colorls
if command -v gem &> /dev/null; then
    COLORLS_PATH="$(dirname $(gem which colorls))"
    if [ -d $COLORLS_PATH ]; then
        source "${COLORLS_PATH}/tab_complete.sh"
    else
        echo "Colorls was not found. Please install it with \"gem install colorls\" or remove it form .zshrc."
    fi
else
    echo "Gem was not found. Please install Ruby."
fi
alias lc='colorls -lA --sd'

# Powerline
# https://github.com/powerline/powerline
# If using Powerline, the zsh theme should be disabled
# https://wiki.archlinux.org/index.php/Powerline
# POWERLINE_SCRIPT="/usr/share/powerline/bindings/zsh/powerline.zsh"
# if [ -f $POWERLINE_SCRIPT ]; then
#     powerline-daemon -q
#     source "/usr/share/powerline/bindings/zsh/powerline.zsh"
# fi

# PowerShell telemetry has to be disabled with an environment variable before starting it.
# https://github.com/PowerShell/PowerShell#telemetry
export POWERSHELL_TELEMETRY_OPTOUT="1"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

# Powerlevel10k configuration
# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Add Snap icons to the launcher
if [ -f "/etc/profile.d/apps-bin-path.sh" ]; then
    emulate sh -c "source /etc/profile.d/apps-bin-path.sh"
fi

# Anaconda can be configured for zsh by running
# "conda init zsh" in a shell that has conda enabled (such as bash)
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('${HOME}/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "${HOME}/anaconda3/etc/profile.d/conda.sh" ]; then
        . "${HOME}/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="${HOME}/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# CERN ROOT
# https://root.cern/
ROOT_SCRIPT="${HOME}/Downloads/root/bin/thisroot.sh"
if [ -f $ROOT_SCRIPT ]; then
    source $ROOT_SCRIPT
fi
