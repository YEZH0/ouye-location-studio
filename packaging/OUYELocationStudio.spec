# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the OUYE Location Studio GUI (windowed).

import tomllib
from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata

# SPECPATH is the directory containing this spec file; the project root is its parent.
ROOT = Path(SPECPATH).resolve().parent  # noqa: F821

version = tomllib.loads(
    (ROOT / "pyproject.toml").read_text(encoding="utf-8")
)["project"]["version"]
version_tuple = tuple(int(part) for part in version.split(".")) + (0,)

datas = [
    (str(ROOT / "LICENSE"), "."),
    (str(ROOT / "THIRD_PARTY_NOTICES.md"), "."),
]
datas += copy_metadata("pymobiledevice3")
datas += copy_metadata("cryptography")
datas += copy_metadata("qrcode")
datas += copy_metadata("Pillow")

hiddenimports = [
    "pymobiledevice3.lockdown",
    "pymobiledevice3.usbmux",
    "pymobiledevice3.service_connection",
    "pymobiledevice3.services.lockdown",
    "pymobiledevice3.exceptions",
]

a = Analysis(
    [str(ROOT / "packaging/entry_gui.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(ROOT / "packaging/build_hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "pandas", "numpy", "jedi", "parso", "tkinter"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="OUYELocationStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
