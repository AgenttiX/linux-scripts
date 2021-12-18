### Installing zsh
Zsh is an awesome shell with the extensive plugin collection
[Oh My Zsh](https://ohmyz.sh/).
You can install and configure it by cd'ing to the root
of this repository and executing the following commands.

``` bash
sudo apt-get update
sudo apt-get install zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
mv ${HOME}/.zshrc ${HOME}/.zshrc-original
ln -s ${PWD}/zsh/.zshrc ${HOME}/.zshrc
ZSH_CUSTOM="${HOME}/.oh-my-zsh/custom2"
ln -s ${PWD}/zsh/custom ${ZSH_CUSTOM}
```

### Additional plugins
[zsh-autocomplete](https://github.com/marlonrichert/zsh-autocomplete),
[zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions)
and
[zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting):
``` bash
mkdir -p ${ZSH_CUSTOM}/plugins
cd ${ZSH_CUSTOM}/plugins
git clone git@github.com:marlonrichert/zsh-autocomplete.git
git clone git@github.com:zsh-users/zsh-autosuggestions.git
git clone git@github.com:zsh-users/zsh-syntax-highlighting.git
```

### Powerlevel10k theme
Installation of the [Powerlevel10k](https://github.com/romkatv/powerlevel10k) theme:
first download all the
[MesloLGS theme files](https://github.com/romkatv/powerlevel10k#meslo-nerd-font-patched-for-powerlevel10k)
and set it as your default terminal font.
Then run the following commands.
``` bash
mkdir -p ${ZSH_CUSTOM}/themes
cd ${ZSH_CUSTOM}/themes
git clone git@github.com:romkatv/powerlevel10k.git
ln -s <LOCAL_REPOSITORY_FOLDER>/linux-scripts/zsh/.p10k.zsh ${HOME}/.p10k.zsh
```

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
