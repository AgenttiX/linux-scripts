# linux-scripts
![CI](https://github.com/AgenttiX/linux-scripts/workflows/CI/badge.svg)
![CodeQL](https://github.com/AgenttiX/linux-scripts/workflows/CodeQL/badge.svg)

A collection of GNU/Linux scripts I've found userful


### Installing services
```
sudo cp myservice.service /etc/systemd/system/myservice.service
sudo chmod 644 /etc/systemd/system/myservice.service
```

Enabling the Syncthing service: `sudo systemctl enable syncthing@myusername.service`


### Installing zsh
Zsh is an awesome shell with the extensive plugin collection [Oh My Zsh](https://ohmyz.sh/).
You can install and configure it by cd'ing to the root of this repository and executing the following commands.

```
sudo apt-get update && sudo apt-get install zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
mv $HOME/.zshrc $HOME/.zshrc-original
ln -s $PWD/zsh/.zshrc $HOME/.zshrc
ln -s $PWD/zsh/custom $HOME/.oh-my-zsh/custom2
```

To install zsh-autosuggestions, please follow the
[instructions](https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md)
from the project repository.
