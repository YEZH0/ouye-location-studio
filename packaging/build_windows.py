"""Build both Windows EXEs with PyInstaller.

Produces ``dist/OUYELocationStudio.exe`` (windowed GUI) and
``dist/ouye-auth-helper.exe`` (console authentication helper), which the GUI
locates next to itself at runtime.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    specs = [
        root / "packaging" / "auth_helper.spec",
        root / "packaging" / "OUYELocationStudio.spec",
    ]
    for spec in specs:
        print(f"[build] PyInstaller {spec.name}")
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", str(spec)],
            cwd=root,
        )
        if result.returncode != 0:
            print(f"[build] FAILED: {spec.name}")
            return result.returncode
    print("[build] Done. Artifacts in dist/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
