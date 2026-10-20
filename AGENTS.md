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
