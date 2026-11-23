# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the authentication helper (console; holds the private key).

from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata

ROOT = Path(SPECPATH).resolve().parent  # noqa: F821

datas = copy_metadata("cryptography")

a = Analysis(
    [str(ROOT / "src/ouye_location_studio/auth_helper.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=["cryptography.hazmat.primitives.serialization.pkcs7"],
    hookspath=[str(ROOT / "packaging/build_hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PySide6", "matplotlib", "pandas", "numpy", "tkinter"],
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
    name="ouye-auth-helper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
