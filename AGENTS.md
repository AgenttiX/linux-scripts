# AGENTS.md

## Repository description
This linux-scripts repository contains various scripts
for automating tasks and configuring software on Linux.
The scripts are grouped in folders based on the software or topic they are related to.

## Environment
- Platform: Kubuntu 26.04

## General instructions
- Prefer solutions that are highly secure.
- For scripts that can be feasibly tested, create unit tests in `./tests`.
- See `README.md` for the repository structure.
- When asked to create a zsh command or function, place it in an appropriate file in `zsh/custom/`.
- Prefer to write complex scripts in Python instead of bash/zsh.

## Code style
- Use Python 3.12+ type hints in Python scripts where possible.
- Prefer to organize modules alphabetically (ignoring the leading underscores)
  with constants first, then classes, and then functions.
  However, the exceptions are that `logger` should be right after the imports, and that `main` should be the last function in a module.
  You may deviate from these if required for e.g. type hints.

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
