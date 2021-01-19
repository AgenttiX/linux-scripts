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


## KDE
### i3-like tiling
Screen space is a very limited resource, especially on laptops.
Therefore it should not be wasted.
With the usual window managers it's rather difficult to position windows efficiently, and consequently a significant fraction of the screen space is wasted.
This can be fixed by using a tiling window manager such as [i3](https://i3wm.org/).
Luckily similar functionality can also be installed on [KDE](https://kde.org/).

Install the [tiling extension](https://store.kde.org/p/1112554) by going to System Settings &#8594; Window Management &#8594; KWin Scripts &#8594; Get New Scripts.
The settings button for the extension does not show up by default, but you can fix this by running the code below.

```
mkdir -p ~/.local/share/kservices5
ln -s ~/.local/share/kwin/scripts/kwin-script-tiling/metadata.desktop ~/.local/share/kservices5/kwin-script-tiling.desktop
```

The following settings are recommended.

- Common options &#8594; Placement method: Open new tiles at the end
- Half layout &#8594; Default master width: 50 %


### Fixing Discord snap log spam
This is discussed in a [GitHub issue](https://github.com/snapcrafters/discord/issues/23).

```
sudo snap connect discord:system-observe :system-observe
```
