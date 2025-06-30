# This file is for environments where it's not possible to change the login shell with chsh.
# Do not use this if you can change your login shell.

# Check that the session is interactive.
# https://askubuntu.com/a/1491731
if [[ $- == *i* ]]; then
    if command -v zsh &> /dev/null; then
        # https://askubuntu.com/a/1292415
        export SHELL=$(which zsh)

        # https://stackoverflow.com/a/10341338
        # https://askubuntu.com/a/525787
        if [[ -o login ]]; then
            exec zsh -l
        else
            exec zsh
        fi

        # The exec command replaces the current shell and therefore terminates the reading of this file.
        # if [ $? -eq 0 ]; then
        #     return 0
        # else
        #     echo "There was an issue in running zsh. Please check your configuration. Dropping to bash shell."
        # fi
    fi
fi
