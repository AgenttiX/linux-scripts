### Installing zsh
Zsh is an awesome shell with the extensive plugin collection
[Oh My Zsh](https://ohmyz.sh/).
You can install it using the `install_zsh.sh` script.


### Additional plugins
[zsh-autocomplete](https://github.com/marlonrichert/zsh-autocomplete),
[zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions)
and
[zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting):


### Powerlevel10k theme
Installation of the [Powerlevel10k](https://github.com/romkatv/powerlevel10k) theme:
first download all the
[MesloLGS theme files](https://github.com/romkatv/powerlevel10k#meslo-nerd-font-patched-for-powerlevel10k)
and set it as your default terminal font.
Then run the `install_zsh.sh` script if you haven't yet run iiiit.


### Stderred
With [stderred](https://github.com/sickill/stderred) you can get stderr displayed in red.
```
# On a multiarch system you may need gcc-multilib as well.
sudo apt install build-essential cmake
# This can be run in a directory of your choice, but my .zshrc presumes that this is located in $HOME/Git.
git clone git://github.com/sickill/stderred.git
cd stderred
make 32
make 64
```

Much of these configuration files is based on
[the ones](https://gitlab.com/tolvanea/linux_utility_scripts/-/blob/master/zshrc) by
[Alpi Tolvanen](https://github.com/tolvanea).
Big thanks to him for introducing me to zsh!
