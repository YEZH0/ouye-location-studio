"""Store user-authorized identities on this Mac, outside the application bundle."""

import os
from pathlib import Path
import stat
import tempfile

from ..auth_helper import CERT_ENV, KEY_ENV, ProviderError, read_identity_file, validate_identity

APP_SUPPORT = Path.home() / "Library/Application Support/OUYE Location Studio"
FILENAMES = ("certificate.p7b", "identity.pk8")


def check_private(path: Path, mode: int, kind) -> None:
    info = path.lstat()
    if not kind(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != mode:
        raise ProviderError("本地认证配置的所有者、文件类型或权限不符合要求")


def local_pair(root: Path, name: str) -> tuple[Path, Path]:
    if not name.startswith("identity-") or Path(name).name != name:
        raise ProviderError("本地认证配置标识无效")
    directory = root / name
    check_private(root, 0o700, stat.S_ISDIR)
    check_private(directory, 0o700, stat.S_ISDIR)
    certificate, key = (directory / filename for filename in FILENAMES)
    for path in (certificate, key):
        check_private(path, 0o600, stat.S_ISREG)
    return certificate, key


def import_identity(root: Path) -> str:
    certificate, key = map(read_identity_file, (CERT_ENV, KEY_ENV))
    validate_identity(certificate, key)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    check_private(root, 0o700, stat.S_ISDIR)
    directory = Path(tempfile.mkdtemp(prefix="identity-", dir=root))
    try:
        for filename, contents in zip(FILENAMES, (certificate, key), strict=True):
            descriptor = os.open(directory / filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(contents)
    except BaseException:
        for filename in FILENAMES:
            (directory / filename).unlink(missing_ok=True)
        directory.rmdir()
        raise
    return directory.name
