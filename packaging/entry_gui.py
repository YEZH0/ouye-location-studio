"""PyInstaller entry point: launches the GUI via absolute import.

``app.py`` itself uses package-relative imports (so ``python -m
ouye_location_studio`` works in source mode); this thin wrapper gives
PyInstaller a top-level script that imports the package normally.
"""

import sys

from ouye_location_studio.app import main

if __name__ == "__main__":
    sys.exit(main())
