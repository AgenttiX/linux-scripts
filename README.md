# Linux scripts
![CI](https://github.com/AgenttiX/linux-scripts/workflows/CI/badge.svg)
![CodeQL](https://github.com/AgenttiX/linux-scripts/workflows/CodeQL/badge.svg)
[![codecov](https://codecov.io/gh/AgenttiX/linux-scripts/branch/master/graph/badge.svg?token=SUMWHTQJW8)](https://codecov.io/gh/AgenttiX/linux-scripts)

This repository contains some GNU/Linux scripts I've found useful.
For my Linux instructions, please see my website at [agx.fi](https://agx.fi/).

## Repository structure
- `android`: Scripts for working with Android devices. Firmware flashing, backup, app installation etc.
- `backup`: Backup scripts
- `crypto`: Cryptocurrency mining
- `drivers`: Scripts for installing drivers
- `games`: Scripts for installing and configuring games and emulators
- `git`: Git configs and scripts, e.g. `pull.py` for pulling all repositories in `~/Git`
- `i3`: i3 window manager configs
- `images`: Scripts for converting images
- `install`: Software installation for Ubuntu-based systems. Includes also Flatpak, Snap and asdf.
  Run `./install/install.py` (or `python3 -m install`) as a normal user. It runs `./install/install_sudo.py` with sudo.
  Add `--sources` to configure the apt repositories as well, e.g. on the first run.
- `iperf`: Scripts for measuring network performance
- `kde`: KDE Plasma configs
- `librenms`: LibreNMS configs
- `luks-tpm`: Scripts for unlocking LUKS encrypted volumes with TPM
- `maintenance`: General system maintenance: updates, cleaning, security scans, TRIM etc.
  Run `./maintenance/__main__.py` (or `python3 -m maintenance`) as a normal user.
  It runs `./maintenance/sudo.py` with sudo for the steps that require root privileges.
  Run with `--help` to see the options, e.g. `--deep` for deep cleaning.
- `neovim`: Neovim configs
- `obs-studio`: OBS Studio configs
- `opentabletdriver`: Graphics tablet driver configs
- `pgp`: PGP configs and utilities, e.g. converting ASCII-armored keys to the binary format
- `physics`: Scripts for installing and configuring various software for physics research
- `proxmox`: Proxmox hypervisor configs
- `pycharm`: PyCharm configs
- `samba`: Scripts for configuring a Samba Active Directory domain member
- `ssh`: SSH configs. `ssh/config.d/` is symlinked to `~/.ssh/config.d/`,
  and `ssh/openssh10.conf` to `~/.ssh/openssh10.conf` on systems with OpenSSH 10.0 or newer.
- `startup`: startup scripts. ` agx_startup.py` is run as root by `agx-startup.service`,
  and `agx-user-startup.sh` is run by `agx-user-startup.desktop` as the current user.
- `testing`: Performance and reliability testing scripts,
  e.g. `sysinfo.py`, which prints the hardware and OS details for a performance testing report
  (`--json` for JSON output, run with sudo for the RAM details that are not available without root access)
- `tests`: Unit tests for the scripts in this repository
- `tmux`: tmux terminal multiplexer configs
- `usbip`: USB/IP configs for passing USB devices over IP
- `utils`: Shared Python utilities for the scripts, e.g. `utils/misc_utils.py`
- `virtualbox`: VirtualBox maintenance scripts
- `vscodium`: VSCodium configs for e.g. SSH remoting
- `wacom`: Custom script for configuring Wacom tablets.
   Requires X11 and doesn't work on Wayland.
   Use Kubuntu's settings GUI or the configs in `opentabletdriver/` instead.
- `wireguard`: WireGuard configs, e.g. autostart script
- `xournalpp`: Xournal++ configs. Symlinked to Xournal++'s config directory.
- `zsh`: zsh configs, e.g. `zsh/.zshrc`, which is symlinked to `~/.zshrc`,
  and `zsh/custom/`, which contains custom zsh commands.

## Configs
These can be symlinked to `~/` where needed.
- `.bashrc`: Bash configuration that switches to zsh.
  For environments where it's not possible to change the login shell with `chsh`.
- `.gdbinit`: GDB (GNU Debugger) config
- `.profile`: Config for login shells
- `.xprofile`: Config for X11 sessions

### Scripts
- `kernel_remover.py`: Remove old kernel versions
- `kubuntu_release_upgrade.sh`: Kubuntu release upgrade script, with proper logging
- `modem.py`: Script for configuring the integrated WWAN modem of ThinkPad laptops


## Python environment
The Python dependencies are managed with [uv](https://docs.astral.sh/uv/).
Run `uv sync` to create the virtual environment in `.venv/`,
and `uv run pytest` to run the unit tests.

## Licensing
[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B5825%2Fgit%40github.com%3AAgenttiX%2Flinux-scripts.git.svg?type=large)](https://app.fossa.com/projects/custom%2B5825%2Fgit%40github.com%3AAgenttiX%2Flinux-scripts.git?ref=badge_large)
