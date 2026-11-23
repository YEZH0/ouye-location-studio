"""Native PyInstaller app with a separate local authentication process."""

import os
from pathlib import Path
import tomllib

from PyInstaller.utils.hooks import copy_metadata

root = Path(SPECPATH).resolve().parent
identity = os.environ.get("OUYE_MAC_CODESIGN_IDENTITY")
version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
notices = [(str(root / name), ".") for name in ("LICENSE", "THIRD_PARTY_NOTICES.md")]

metadata = []
for package in ("pymobiledevice3", "apple_compress", "qrcode", "Pillow", "cryptography"):
    metadata.extend(copy_metadata(package))

gui = Analysis(
    [str(root / "packaging/entry_macos.py")],
    pathex=[str(root / "src")],
    datas=notices + metadata,
    excludes=["matplotlib", "pandas", "numpy", "tkinter"],
)
helper = Analysis(
    [str(root / "src/ouye_location_studio/auth_helper.py")],
    excludes=["PySide6"],
)
gui_exe = EXE(
    PYZ(gui.pure), gui.scripts, [], exclude_binaries=True,
    name="OUYE Location Studio", console=False, codesign_identity=identity,
)
helper_exe = EXE(
    PYZ(helper.pure), helper.scripts, [], exclude_binaries=True,
    name="ouye-auth-helper", console=True, codesign_identity=identity,
)
files = COLLECT(
    gui_exe, helper_exe, gui.binaries, helper.binaries, gui.datas, helper.datas,
    name="OUYE-macos-staging",
)
app = BUNDLE(
    files, name="OUYE Location Studio.app",
    bundle_identifier="xyz.yezhihong.ouye-location-studio",
    version=version,
    codesign_identity=identity,
    info_plist={"NSHighResolutionCapable": True},
)
