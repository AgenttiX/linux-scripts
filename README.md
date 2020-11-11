# linux-scripts
![CodeQL](https://github.com/AgenttiX/linux-scripts/workflows/CodeQL/badge.svg)

A collection of GNU/Linux scripts I've found userful


### Installing services
```
sudo cp myservice.service /etc/systemd/system/myservice.service
sudo chmod 644 /etc/systemd/system/myservice.service
```

Enabling the Syncthing service: `sudo systemctl enable syncthing@myusername.service`
