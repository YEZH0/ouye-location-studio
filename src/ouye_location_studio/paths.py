"""Runtime path resolution (source vs. frozen EXE)."""

from __future__ import annotations

import sys
from pathlib import Path


def auth_helper_path() -> str:
    """Return the authentication helper executable/script for this runtime.

    In a PyInstaller bundle the helper is a separate console EXE placed next to
    the GUI executable; in source mode it is the bundled Python module.
    """
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).resolve().parent / "ouye-auth-helper.exe"
        if exe.is_file():
            return str(exe)
    return str(Path(__file__).resolve().parent / "auth_helper.py")
