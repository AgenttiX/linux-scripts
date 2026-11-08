"""Install all the software by running install.py.

Usage: ``python3 -m install [arguments]`` in the repository directory, or ``python3 install [arguments]``.
The arguments are passed to install.py.
"""

import pathlib
import sys

# Allow running this directory directly with "python3 install".
# The repository directory has to be first, as this directory contains install.py, which would shadow the package.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from install import install

if __name__ == "__main__":
    install.main()
