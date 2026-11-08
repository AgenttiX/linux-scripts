# AGENTS.md

## Repository description
This linux-scripts repository contains various scripts
for automating tasks and configuring software on Linux.
The scripts are grouped in folders based on the software or topic they are related to.

## Commands
- Install dependencies: `uv sync`
- Upgrade locked dependency versions: `uv lock --upgrade`
- Run tests: `uv run pytest`
- Python lint: `uv run ruff check`
- Type checking: `uv run pyrefly check`
- Type coverage checking: `uv run pyrefly coverage check`
- Bash lint: `shellcheck <filename.sh>`

## Environment
- Platforms:
  - Kubuntu 26.04 desktops and laptops: for most scripts
  - Ubuntu 26.04 servers: for headless scripts
  - Steam Frame (VR headset): where relevant and feasible
    (ARM64, SteamOS, based on Arch Linux, KDE Plasma, read-only root partition, package installation primarily with Flatpak)
- Keep backwards compatibility with Ubuntu 24.04 where feasible.
- Python version: 3.12+

## General instructions
- Prefer solutions that are highly secure.
- For scripts that can be feasibly tested, create unit tests in `./tests`.
- See `README.md` for the repository structure.
- When asked to create a zsh command or function, place it in an appropriate file in `zsh/custom/`.
- Prefer to write complex scripts in Python instead of bash/zsh.
  If the user asks you to create a bash/zsh script that turns out to be longer than a few lines, consider writing it in Python instead.
- This repository is public. Do not commit sensitive information in this repository.
- You may commit directly on the `master` branch. Don't push unless the user explicitly asks you to.

## Code style
- Use Python 3.12+ type hints in Python scripts where possible.
- Prefer modern coding practices. You may use `__future__` imports.
- Prefer to organize modules alphabetically (ignoring the leading underscores)
  with constants first, then classes, and then functions.
  However, the exceptions are that `logger` should be right after the imports, and that `main` should be the last function in a module.
  You may deviate from these if required for e.g. type hints.
- Use `frozen=True, slots=True` for dataclasses where feasible.

## Docstring conventions
- Use the Sphinx docstring format.
- Use `:param:`, `:return:` and `:raises:`, where appropriate.

## Related repositories
If the repositories below are not available locally when you need them,
`git clone` them in the same parent directory as this repository using SSH.
You may edit the local copies as needed, if no other agent sessions are currently working on them,
and if they don't have large uncommitted changes.

- [Personal website](https://github.com/AgenttiX/agenttix.github.io): `../agenttix.github.io`
  - The website is available at [agx.fi](https://agx.fi/) and published automatically from its GitHub repository.
  - When editing this or other repositories, check that the information on the website is consistent with the edits.
    If not, update the website accordingly. Don't push your edits in the website repository unless asked.
- [agx-ai](https://github.com/AgenttiX/agx-ai): `../agx-ai`, personal AI server and client configs
- [openwrt-scripts](https://github.com/AgenttiX/openwrt-scripts): `../openwrt-scripts`, scripts for OpenWRT-based systems
- [private-scripts](https://github.com/AgenttiX/private-scripts): `../private-scripts`
  - Personal SSH and Git configuration etc. Not public.
  - All scripts that contain personal hostnames other non-public information go in `../private-scripts`.
- [windows-scripts](https://github.com/AgenttiX/windows-scripts): `../windows-scripts`
  - The Windows equivalent of this `linux-scripts` repository.
