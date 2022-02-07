#!/usr/bin/env zsh

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

# Fix Pythia 8 Python bindings
if [ -d "/usr/local/share/Pythia8/" ]; then
    export PYTHONPATH="${PYTHONPATH}:/usr/local/lib"
fi
