"""Utilities for unit tests."""

import importlib.util
import pathlib
import types

REPO_PATH = pathlib.Path(__file__).resolve().parent.parent
KILL_ZSH = REPO_PATH / "zsh" / "custom" / "kill.zsh"
UTILS_ZSH = REPO_PATH / "zsh" / "custom" / "utils.zsh"


def load_module(name: str, path: pathlib.Path) -> types.ModuleType:
    """Load a Python script that is not part of an importable package.

    :param name: name for the module
    :param path: path to the script
    :return: the loaded module
    :raises ImportError: if the script cannot be loaded
    """
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        msg = f"Could not load {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
