# linux-scripts
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
mv ~/.zshrc ~/.zshrc-original
ln -s ./zsh/.zshrc ~/.zshrc
mv ~/.oh-my-zsh/custom ~/.oh-my-zsh/custom-original
ln -s ./zsh/custom ~/.oh-my-zsh/custom
```
