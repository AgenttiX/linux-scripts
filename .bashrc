# This file is for environments where it's not possible to change the login shell with chsh.
# Do not use this if you can change your login shell.

# Check that the session is interactive.
# https://askubuntu.com/a/1491731
if [[ $- == *i* ]]; then
    if command -v zsh &> /dev/null; then
        # https://askubuntu.com/a/1292415
        export SHELL=`which zsh`
        zsh
    fi
fi
