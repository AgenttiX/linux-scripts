# linux-scripts
![CI](https://github.com/AgenttiX/linux-scripts/workflows/CI/badge.svg)
![CodeQL](https://github.com/AgenttiX/linux-scripts/workflows/CodeQL/badge.svg)
[![codecov](https://codecov.io/gh/AgenttiX/linux-scripts/branch/master/graph/badge.svg?token=SUMWHTQJW8)](https://codecov.io/gh/AgenttiX/linux-scripts)

A collection of GNU/Linux scripts I've found userful


### Installing services
```
sudo cp myservice.service /etc/systemd/system/myservice.service
sudo chmod 644 /etc/systemd/system/myservice.service
```

Enabling the Syncthing service:
`sudo systemctl enable syncthing@myusername.service`


### Installing zsh
Zsh is an awesome shell with the extensive plugin collection
[Oh My Zsh](https://ohmyz.sh/).
You can install and configure it by cd'ing to the root
of this repository and executing the following commands.

```
sudo apt-get update
sudo apt-get install zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
mv ${HOME}/.zshrc ${HOME}/.zshrc-original
ln -s ${PWD}/zsh/.zshrc ${HOME}/.zshrc
ZSH_CUSTOM="${HOME}/.oh-my-zsh/custom2"
ln -s ${PWD}/zsh/custom ${ZSH_CUSTOM}
```

Installation of additional plugins,
[zsh-autocomplete](https://github.com/marlonrichert/zsh-autocomplete)
and
[zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions):
```
mkdir -p ${ZSH_CUSTOM}/plugins
cd ${ZSH_CUSTOM}/plugins
git clone git@github.com:marlonrichert/zsh-autocomplete.git
git clone git@github.com:zsh-users/zsh-autosuggestions.git
```
