# Proton configurations

### General
Adjusting Wine/Proton configs
``` bash
protontrics <game_id> winecfg
```

If you mess up the settings of a game, you can reset its Proton configs with:
``` bash
rm ~/.steam/steam/steamapps/compatdata/<game_id>
```

Virtual desktop:
[TODO](https://www.reddit.com/r/Lutris/comments/qyw3eb/launching_game_shows_empty_blue_wine_desktop/)

### Among Us
Launch options:
``` bash
PROTON_NO_ESYNC=1 PROTON_USE_WINED3D=1 %command%
```

### Final Fantasy XIV Online
These instructions are based on [this](https://www.protondb.com/app/39210#lH6119S8yp) ProtonDB comment.
Create your account on the [Square Enix website](https://secure.square-enix.com/account/app/svc/ffxivregister?lng=en-us) or a Windows installation of the game.
Don't use the Linux installation for the account creation, or you may not be able to login for 24 hours.
Download the game and open it once.
You should get a buggy window.
Close it and then run `ffxiv.sh`.
Open the launcher.
The login button of the launcher does not work, but you can press enter to log in.
Click play to launch the game, and then close it.
If you try to play, you should get a black screen.
Run `ffxiv.sh` again.
The game should now be ready to play.

### LEGO Lord of the Rings
The game requires DirectX 9 to be installed:
``` bash
protontricks 214510 d3dx9_41
```
<!--
If you have a multi-monitor setup and want to run the game on a secondary monitor:
``` bash
protontricks 214510 winecfg
```
-->
[ProtonDB](https://www.protondb.com/app/214510),
[GitHub](https://github.com/ValveSoftware/Proton/issues/1836)
