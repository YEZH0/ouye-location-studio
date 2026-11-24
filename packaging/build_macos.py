"""Build the native macOS APP and optionally create a compressed DMG."""

import argparse
from pathlib import Path
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dmg", action="store_true")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("Run this script on macOS with a native Python environment.")

    root = Path(__file__).resolve().parent.parent
    dist = root / "dist/macos"
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm",
         "--distpath", str(dist), "--workpath", str(root / "build/macos"),
         str(root / "packaging/OUYELocationStudio-macos.spec")],
        cwd=root, check=True,
    )
    app = dist / "OUYE Location Studio.app"
    subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)], check=True)
    if args.dmg:
        subprocess.run(
            ["hdiutil", "create", "-ov", "-format", "UDZO", "-volname",
             "OUYE Location Studio", "-srcfolder", str(app),
             str(dist / "OUYE Location Studio.dmg")],
            check=True,
        )


if __name__ == "__main__":
    main()
