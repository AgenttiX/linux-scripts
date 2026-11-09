#!/usr/bin/env python3

"""Configure Git with the shared config of this directory and a private config.

Usage: ``python3 -m git <path to the private Git config>`` in the repository directory.
See ``configure.py`` for details.
"""

import pathlib
import sys

# Allow running this file directly as a script.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from git import configure

if __name__ == "__main__":
    sys.exit(configure.main())
